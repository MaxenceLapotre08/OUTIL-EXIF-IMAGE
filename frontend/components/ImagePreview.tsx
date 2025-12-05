'use client';

import { useEffect, useState } from 'react';
import Image from 'next/image';

interface ImagePreviewProps {
    file: File | null;
}

export function ImagePreview({ file }: ImagePreviewProps) {
    const [previewUrl, setPreviewUrl] = useState<string | null>(null);

    useEffect(() => {
        if (!file) {
            setPreviewUrl(null);
            return;
        }

        const url = URL.createObjectURL(file);
        setPreviewUrl(url);

        return () => {
            URL.revokeObjectURL(url);
        };
    }, [file]);

    if (!previewUrl) {
        return null;
    }

    return (
        <div className="space-y-3">
            <h3 className="text-sm font-medium text-foreground">Image Preview</h3>
            <div className="glass rounded-xl overflow-hidden aspect-video relative group">
                <Image
                    src={previewUrl}
                    alt="Preview"
                    fill
                    className="object-contain group-hover:scale-105 transition-transform duration-300"
                />
            </div>
        </div>
    );
}
