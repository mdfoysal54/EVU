export type User = { id: number; email: string };
export type Conversation = { id: number; title: string; created_at: string };
export type Message = { id: number; role: string; content: string; created_at: string };
export type ChatResponse = { response: string; provider: string; model?: string | null; rag_used: boolean; sources: Array<{ document_id:number; filename:string; chunk_index:number; score:number }> };
export type Provider = { id:string; name:string; available:boolean; default_model:string };
