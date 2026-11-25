import {useState} from 'react'
import type {DashboardComplaint,ReviewStatus} from '../types'
import ComplaintForm from '../components/ComplaintForm'
import CsvUpload from '../components/CsvUpload'
import ComplaintReviewTable from '../components/ComplaintReviewTable'
import ComplaintDetail from '../components/ComplaintDetail'
export default function ComplaintsPage({onRefresh,selected,onSelect,onReviewUpdated}:{onRefresh:()=>void;selected:DashboardComplaint|null;onSelect:(c:DashboardComplaint|null)=>void;onReviewUpdated:(status:ReviewStatus)=>void}){const[tableVersion,setTableVersion]=useState(0);return <><section className="collection-layout"><div className="stack"><ComplaintForm onSaved={onRefresh}/><CsvUpload onDone={onRefresh}/></div><ComplaintReviewTable key={tableVersion} onSelect={onSelect}/></section>{selected&&<ComplaintDetail item={selected} onClose={()=>onSelect(null)} onUpdated={status=>{onReviewUpdated(status);setTableVersion(v=>v+1)}}/>}</>}
