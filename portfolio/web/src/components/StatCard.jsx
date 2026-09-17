export default function StatCard({ label, value }) {
  return (
    <div className="card stat">
      <div className="stat-value">{value}</div>
      <div className="footnote">{label}</div>
    </div>
  )
}
