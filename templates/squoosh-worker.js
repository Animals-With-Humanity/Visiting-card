import { encode } from "https://unpkg.com/@squoosh/lib@latest";

self.onmessage = async (event) => {
    const { file, quality } = event.data;

    const imageBitmap = await createImageBitmap(file);
    const encoder = new encode.WebPEncoder();
    encoder.configure({ quality });

    const compressedImage = await encoder.encode(imageBitmap);
    const compressedBlob = new Blob([compressedImage], { type: "image/webp" });

    self.postMessage(compressedBlob);
};
