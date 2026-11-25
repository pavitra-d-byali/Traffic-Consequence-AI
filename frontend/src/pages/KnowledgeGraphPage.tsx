import type {GraphData} from '../types'
import GraphSummary from '../components/GraphSummary'
import HotspotList from '../components/HotspotList'
export default function KnowledgeGraphPage({data}:{data:GraphData|null}){return <section className="graph-layout"><GraphSummary data={data}/><HotspotList data={data}/></section>}
