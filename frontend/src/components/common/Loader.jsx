function Loader({ fullScreen = false }) {
  if (fullScreen) {
    return (
      <div className="loader-overlay">
        <div className="loader-spinner" />
      </div>
    )
  }

  return <div className="loader-spinner" />
}

export default Loader