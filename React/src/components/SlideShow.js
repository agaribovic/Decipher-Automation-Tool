import Carousel from 'react-gallery-carousel';
import 'react-gallery-carousel/dist/index.css';

const Slideshow = () => {

    const images = [9, 8, 7, 6, 5].map((number) => ({
        src: `https://placedog.net/${number}00/${number}00?id=${number}`
      }));

      return (
        <div id="gallery">
          <Carousel images={images} style={{ height: 1000, width: 1500}} />
        </div>
      );

}

export default Slideshow;
