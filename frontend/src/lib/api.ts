import { config } from "./config";
import { clearToken, getToken } from "./storage";

export class ApiError extends Error {
  status: number; detail: unknown;
  constructor(status:number, detail:unknown) { super(typeof detail === "string" ? detail : `EVU API error (${status})`); this.status=status; this.detail=detail; }
}

export function apiUrl(path:string) {
  const normalized = path.startsWith("/") ? path : `/${path}`;
  return `${config.apiUrl}${normalized.startsWith(config.apiPrefix) ? normalized : `${config.apiPrefix}${normalized}`}`;
}

async function parseResponse(response: Response) {
  const text = await response.text();
  if (!text) return null;
  try { return JSON.parse(text); } catch { return text; }
}

export async function apiFetch<T>(path:string, init:RequestInit = {}):Promise<T> {
  const headers = new Headers(init.headers);
  if (init.body && !(init.body instanceof FormData) && !headers.has("Content-Type")) headers.set("Content-Type", "application/json");
  const token = getToken();
  if (token) headers.set("Authorization", `Bearer ${token}`);
  const response = await fetch(apiUrl(path), { ...init, headers, cache:"no-store" });
  const data = await parseResponse(response);
  if (response.status === 401 && typeof window !== "undefined") clearToken();
  if (!response.ok) throw new ApiError(response.status, data?.detail ?? data ?? response.statusText);
  return data as T;
}
export const apiGet = <T,>(path:string) => apiFetch<T>(path);
export const apiPost = <T,>(path:string, body:unknown) => apiFetch<T>(path,{method:"POST",body:JSON.stringify(body)});
export const apiPatch = <T,>(path:string, body:unknown) => apiFetch<T>(path,{method:"PATCH",body:JSON.stringify(body)});
export const apiDelete = <T=unknown,>(path:string) => apiFetch<T>(path,{method:"DELETE"});

export async function login(email:string,password:string) {
  const body = new URLSearchParams(); body.set("username",email); body.set("password",password);
  return apiFetch<{access_token:string;token_type:string}>("/auth/login",{method:"POST",headers:{"Content-Type":"application/x-www-form-urlencoded"},body});
}

export async function uploadDocument(file:File) {
  const form = new FormData(); form.append("file",file);
  return apiFetch("/documents/upload",{method:"POST",body:form});
}

export async function streamConversation(conversationId:number, payload:unknown, onDelta:(delta:string)=>void, onDone:(meta:any)=>void) {
  const token=getToken();
  const response=await fetch(apiUrl(`/conversations/${conversationId}/stream`),{method:"POST",headers:{"Content-Type":"application/json",...(token?{Authorization:`Bearer ${token}`}:{})},body:JSON.stringify(payload)});
  if(!response.ok) throw new ApiError(response.status,await response.text());
  if(!response.body) throw new Error("Streaming response body is unavailable.");
  const reader=response.body.getReader(); const decoder=new TextDecoder(); let buffer="";
  while(true){const {value,done}=await reader.read(); if(done)break; buffer+=decoder.decode(value,{stream:true}); const events=buffer.split("\n\n"); buffer=events.pop()||""; for(const event of events){const line=event.split("\n").find(x=>x.startsWith("data:")); if(!line)continue; const raw=line.slice(5).trim(); if(raw==="[DONE]")continue; try{const data=JSON.parse(raw); if(data.delta)onDelta(data.delta); if(data.done)onDone(data); if(data.error)throw new Error(data.error);}catch(e){if(e instanceof SyntaxError)continue; throw e;}}}
}
