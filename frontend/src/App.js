import React from 'react';
import './background.jpg';
import './App.css';

function App() {

  const openStremioAddon = () => {
    const addonManifestUrl = "stremio://stremio-addon-lxib.onrender.com/manifest.json";
    window.location.href = addonManifestUrl;
  };
  return (
    <>
      <nav className='navbar'>
        <div className='container-fluid'>
          <a href="/" className='navbar-brand bebas-neue-regular'>Streaks Movies</a>
        </div>
      </nav>
      <div className="container-fluid text-light">
        <div className="container-fluid d-flex justify-content-start h-100">
          <div className="text-start">
            <h1 className="display-4 fw-bold">Unlimited movies, TV shows, and more</h1>
            <p>Add-on for Streaming Indian Regional Movies</p>
            <button className="btn text-light btn-lg" onClick={openStremioAddon}>GET ADDON FOR FREE</button>
            <p className="mt-2">Get <a href="https://www.stremio.com/downloads">STREMIO</a> to use this Add-on</p>          
          </div>
        </div>
      </div>
    </>
  );
}

export default App;

/*
<div className="container d-flex justify-content-center align-items-center min-vh-100">
        <div className="login-container">
          <h3 className="text-left mb-4">Welcome to Streaks Movies</h3>
          <p className='text-center mb-4' style={{fontSize:"20px"}}>Add-on for Streaming Indian Regional Movies.</p>
          <p className='mb-4'><b>Supported types:</b> Movies</p>
          <form className="login-form">
            <div className='text-center'>
              <button className='btn btn-outline-primary' onClick={openStremioAddon}>Install Addon</button>
            </div>
            <div className="alert alert-warning mt-4" role="alert">
              <strong>Disclaimer:</strong> Using third-party addons will always be subject to your responsibility
              and the governing law of the jurisdiction you are located.           
            </div>
          </form>
        </div>
      </div>
*/
