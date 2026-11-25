import type {Complaint} from '../types'
import ComplaintList from '../components/ComplaintList'
import AnalysisResult from '../components/AnalysisResult'
export default function AnalysisPage({items,loading,error,selected,onSelect}:{items:Complaint[];loading:boolean;error:string;selected:Complaint|null;onSelect:(c:Complaint)=>void}){return <section className="layout analysis-layout"><div><div className="section-heading"><div><p className="eyebrow">ORIGINAL REPORTS</p><h2>Select a complaint</h2></div></div><ComplaintList items={items} loading={loading} error={error} onSelect={onSelect}/></div><AnalysisResult item={selected}/></section>}
