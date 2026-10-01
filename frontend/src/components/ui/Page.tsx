export function Page({title,description,children,actions}:{title:string;description?:string;children:React.ReactNode;actions?:React.ReactNode}){return <section className="page"><div className="page-head"><div><h1>{title}</h1>{description&&<p>{description}</p>}</div>{actions}</div>{children}</section>}
export function Card({children,className=""}:{children:React.ReactNode;className?:string}){return <div className={`card ${className}`}>{children}</div>}
export function Empty({text}:{text:string}){return <div className="empty">{text}</div>}
export function Loading(){return <div className="empty">Loading…</div>}
