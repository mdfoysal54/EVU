"use client";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { Bot, Boxes, BrainCircuit, Database, FileText, GitBranch, Globe, LayoutDashboard, LogOut, Network, Search, Settings, Shield, Workflow } from "lucide-react";
import { clearToken } from "@/lib/storage";

const nav=[
 ["Dashboard","/dashboard",LayoutDashboard],["Chat","/chat",Bot],["Conversations","/conversations",Database],["Memory","/memory",BrainCircuit],["Documents","/documents",FileText],["Research","/research",Search],["Web Research","/research/web",Globe],["Agents","/agents",Boxes],["Tools","/tools",Network],["Workflows","/workflows",Workflow],["Diagrams","/diagrams",GitBranch],["Models","/models",Boxes],["Security","/security",Shield],["Settings","/settings",Settings],
] as const;
export default function AppShell({children}:{children:React.ReactNode}){const path=usePathname();const router=useRouter();function logout(){clearToken();router.push("/login");}return <div className="app-shell"><aside className="sidebar"><div className="brand"><span className="brand-mark">E</span><div><strong>EVU</strong><small>AI Meta-Orchestrator</small></div></div><nav>{nav.map(([label,href,Icon])=><Link key={href} href={href} className={path===href||path.startsWith(href+"/")?"nav-link active":"nav-link"}><Icon size={17}/><span>{label}</span></Link>)}</nav><button className="nav-link logout" onClick={logout}><LogOut size={17}/><span>Sign out</span></button></aside><main className="main"><header className="topbar"><span className="crumb">EVU Workspace</span><span className="status-dot">Backend connected at {process.env.NEXT_PUBLIC_API_URL||"localhost:8000"}</span></header>{children}</main></div>}
