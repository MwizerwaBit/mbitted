import { Component } from 'react'

/**
 * Catches render/lifecycle errors anywhere below it and shows a friendly
 * fallback instead of a blank screen.
 */
export default class ErrorBoundary extends Component {
  constructor(props) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError() {
    return { hasError: true }
  }

  componentDidCatch(error, info) {
    // Log for debugging / error tracking. `info.componentStack` points at the
    // failing subtree.
    console.error('Uncaught render error:', error, info)
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="container section">
          <p className="empty error">
            Something went wrong while rendering this page.
          </p>
          <button className="button" onClick={() => window.location.reload()}>
            Reload
          </button>
        </div>
      )
    }
    return this.props.children
  }
}
