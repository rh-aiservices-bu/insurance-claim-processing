import * as React from 'react';
import axios from 'axios';
import { useParams } from 'react-router-dom';
import ImageGallery from "react-image-gallery";
import config from '@app/config';


interface Image {
    image_name: string;
    image_key: string;
}

interface ImageCarouselProps {
    images: Image[];
}

const ImageCarousel: React.FunctionComponent<ImageCarouselProps> = ({ images }) => {
    const transformedImages = images.map(image => ({
        original: config.backend_api_url + "/images/" + image.image_key,
        thumbnail: config.backend_api_url + "/images/" + image.image_key,
        thumbnailClass: "image-gallery-thumbnail",
        originalClass: "image-gallery-original",
    }));
    return (
        <ImageGallery items={transformedImages} />
    );
}

export { ImageCarousel };
