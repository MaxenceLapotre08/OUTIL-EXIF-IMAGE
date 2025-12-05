import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface ProcessImageRequest {
    file: File;
    address: string;
    format: 'jpeg' | 'png' | 'webp';
}

export interface CoordinatesResponse {
    address: string;
    latitude: number;
    longitude: number;
}

export const api = {
    /**
     * Process an image: add GPS metadata and convert format
     */
    async processImage(data: ProcessImageRequest): Promise<Blob> {
        const formData = new FormData();
        formData.append('file', data.file);
        formData.append('address', data.address);
        formData.append('format', data.format);

        const response = await axios.post(`${API_URL}/process-image`, formData, {
            responseType: 'blob',
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });

        return response.data;
    },

    /**
     * Get GPS coordinates for an address
     */
    async getCoordinates(address: string): Promise<CoordinatesResponse> {
        const formData = new FormData();
        formData.append('address', address);

        const response = await axios.post<CoordinatesResponse>(
            `${API_URL}/get-coordinates`,
            formData
        );

        return response.data;
    },

    /**
     * Health check
     */
    async healthCheck(): Promise<{ status: string }> {
        const response = await axios.get<{ status: string }>(`${API_URL}/health`);
        return response.data;
    },
};
