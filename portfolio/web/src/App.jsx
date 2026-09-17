import { lazy, Suspense } from 'react'
import { Route, Routes } from 'react-router-dom'
import Layout from './components/Layout.jsx'
import Skeleton from './components/Skeleton.jsx'
import Home from './pages/Home.jsx'
import Blog from './pages/Blog.jsx'
import NotFound from './pages/NotFound.jsx'

// Code-split the heavier routes so the initial bundle stays small (faster
// first paint). BlogPost pulls in the `marked` parser; Dashboard pulls in the
// editor — neither is needed to render the home page.
const BlogPost = lazy(() => import('./pages/BlogPost.jsx'))
const Dashboard = lazy(() => import('./pages/Dashboard.jsx'))

function PageLoader() {
  return (
    <div className="container section" aria-busy="true" aria-label="Loading page">
      <span className="skeleton skeleton-title" aria-hidden="true" />
      <div style={{ height: 16 }} />
      <Skeleton variant="lines" lines={4} />
    </div>
  )
}

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<Home />} />
        <Route path="blog" element={<Blog />} />
        <Route
          path="blog/:slug"
          element={
            <Suspense fallback={<PageLoader />}>
              <BlogPost />
            </Suspense>
          }
        />
        <Route
          path="dashboard"
          element={
            <Suspense fallback={<PageLoader />}>
              <Dashboard />
            </Suspense>
          }
        />
        <Route path="*" element={<NotFound />} />
      </Route>
    </Routes>
  )
}
