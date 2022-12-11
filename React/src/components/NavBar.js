import React from "react";
import "bootstrap/dist/css/bootstrap.min.css";
import { Link } from 'react-router-dom';
                   
const Navbar = () => {
    return (
      <nav className="navbar navbar-expand-lg navbar-dark bg-dark">
        <a className="navbar-brand" href="#">
          Navbar
        </a>
        <button
          className="navbar-toggler"
          type="button"
          data-toggle="collapse"
          data-target="#navbarNavDropdown"
          aria-controls="navbarNavDropdown"
          aria-expanded="false"
          aria-label="Toggle navigation"
        >
          <span className="navbar-toggler-icon"></span>
        </button>

        <div className="collapse navbar-collapse" id="navbarNavDropdown">
          <ul className="navbar-nav">
          <Link to="/">
            <li className="nav-item active">
              <a className="nav-link" href="#">
                Home <span className="sr-only">(current)</span>
              </a>
            </li>
            </Link>
            <Link to="/features">
            <li className="nav-item">
              <a className="nav-link" href="#">
                Features
              </a>
            </li>
            </Link>
            <Link to="/semaphore">
            <li className="nav-item">
              <a className="nav-link" href="#">
                Semaphore
              </a>
            </li>
            </Link>
            <Link to="/api">
            <li className="nav-item">
              <a className="nav-link" href="#">
                API
              </a>
            </li>
            </Link>
          </ul>
        </div>      
      </nav>
    );
  };
  
  export default Navbar;