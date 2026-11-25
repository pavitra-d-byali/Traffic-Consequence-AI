import {useState} from 'react'
import {Activity,Brain,LayoutDashboard,MapPinned,Plus,RefreshCw} from 'lucide-react'
import {api} from './api/client'
import type {DashboardComplaint} from './types'
import ComplaintsPage from './pages/ComplaintsPage'
import DashboardOverviewPage from './pages/DashboardOverviewPage'
import MapHotspotsPage from './pages/MapHotspotsPage'
import AISummariesPage from './pages/AISummariesPage'
type Tab='overview'|'complaints'|'map'|'summaries'
export default function App(){const[tab,setTab]=useState<Tab>('overview'),[selected,setSelected]=useState<DashboardComplaint|null>(null),[refreshCount,setRefreshCount]=useState(0),[notice,setNotice]=useState('')
function refresh(){setRefreshCount(v=>v+1)}
async function seed(){setNotice('');try{const r=await api.seed();setNotice(`${r.label}: ${r.inserted} inserted, ${r.skipped_existing} existing.`);refresh()}catch(e){setNotice(e instanceof Error?e.message:'Could not load demo data')}}
return <main><header className="top"><div className="brand"><div className="brand-icon"><Activity/></div><div><div className="eyebrow">TRAFFIC CONSEQUENCE AI</div><span>Authority review · decision support prototype</span></div></div><div className="top-actions"><button className="secondary" onClick={seed}>Load synthetic demo</button><button className="icon-button" onClick={refresh} aria-label="Refresh dashboard"><RefreshCw size={17}/></button></div></header>{notice&&<div className="notice">{notice}</div>}<nav>{([['overview',LayoutDashboard,'Overview'],['complaints',Plus,'Complaints'],['map',MapPinned,'Map & Hotspots'],['summaries',Brain,'AI Summaries']] as const).map(([id,Icon,label])=><button key={id} className={tab===id?'active':''} onClick={()=>setTab(id)}><Icon size={16}/>{label}</button>)}</nav>{tab==='overview'&&<DashboardOverviewPage key={refreshCount} onOpenComplaint={c=>{setSelected(c);setTab('complaints')}}/>}{tab==='complaints'&&<ComplaintsPage key={refreshCount} onRefresh={refresh} selected={selected} onSelect={setSelected} onReviewUpdated={status=>setSelected(c=>c?{...c,review_status:status}:c)}/ >}{tab==='map'&&<MapHotspotsPage key={refreshCount}/ >}{tab==='summaries'&&<AISummariesPage key={refreshCount}/>}<footer><span>Decision support prototype · no automatic traffic-control actions</span><a href="http://localhost:8000/docs" target="_blank">API docs ↗</a></footer></main>}
