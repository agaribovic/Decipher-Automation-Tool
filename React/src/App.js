import './App.css';
import Slideshow from './components/SlideShow.js';
import Navbar from './components/NavBar.js';
import Features from './components/Features.js';
import Semaphore from './components/Semaphore.js';
import GetApi from './components/Api.js';
import { BrowserRouter, Routes, Route } from "react-router-dom";

function App() {

  return (
    <div className="App">
   <BrowserRouter>
      <Navbar />
      <Routes>
          <Route path="/" element={<Slideshow />} />
          <Route path="*" element={<img src="404.jpg" style={{width: '100%', height: '100%'}}/>} />
          <Route path="features" element={<Features />} />
          <Route path="semaphore" element={<Semaphore/>} />
          <Route path="api" element={<GetApi />} /> 
      </Routes>
    </BrowserRouter>
    </div>
  );
}

export default App;
