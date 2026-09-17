export default function PostCard({ post }) {
  const date = new Date(post.published_at).toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })

  return (
    <article className="card">
      <h2 className="title">{post.title}</h2>
      <p className="summary">{post.summary}</p>
      <time className="footnote" dateTime={post.published_at}>
        {date}
      </time>
    </article>
  )
}
