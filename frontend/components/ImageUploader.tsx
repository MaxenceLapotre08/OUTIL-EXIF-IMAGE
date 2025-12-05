'use client';

import { useState, useCallback } from 'react';
import { Upload, Image as ImageIcon } from 'lucide-react';
import { cn } from '@/lib/utils';

interface ImageUploaderProps {
    onImageSelected: (file: File) => void;
    selectedImage: File | null;
}

export function ImageUploader({ onImageSelected, selectedImage }: ImageUploaderProps) {
    const [isDragging, setIsDragging] = useState(false);

    const handleDragOver = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(true);
    }, []);

    const handleDragLeave = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);
    }, []);

    const handleDrop = useCallback(
        (e: React.DragEvent) => {
            e.preventDefault();
            setIsDragging(false);

            const files = Array.from(e.dataTransfer.files);
            const imageFile = files.find((file) => file.type.startsWith('image/'));

            if (imageFile) {
                onImageSelected(imageFile);
            }
        },
        [onImageSelected]
    );

    const handleFileInput = useCallback(
        (e: React.ChangeEvent<HTMLInputElement>) => {
            const files = e.target.files;
            if (files && files[0]) {
                onImageSelected(files[0]);
            }
        },
        [onImageSelected]
    );

    return (
        <div
            className={cn(
                'upload-zone relative rounded-xl p-12 text-center cursor-pointer group',
                isDragging && 'drag-over'
            )}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={() => document.getElementById('file-input')?.click()}
        >
            <input
                id="file-input"
                type="file"
                accept="image/*"
                className="hidden"
                onChange={handleFileInput}
            />

            <div className="flex flex-col items-center gap-4">
                {selectedImage ? (
                    <>
                        <div className="w-20 h-20 rounded-full bg-primary/20 flex items-center justify-center group-hover:scale-110 transition-transform">
                            <ImageIcon className="w-10 h-10 text-primary" />
                        </div>
                        <div className="space-y-2">
                            <p className="text-lg font-semibold text-foreground">
                                {selectedImage.name}
                            </p>
                            <p className="text-sm text-muted-foreground">
                                {(selectedImage.size / 1024 / 1024).toFixed(2)} MB
                            </p>
                            <p className="text-xs text-muted-foreground">
                                Click to change image
                            </p>
                        </div>
                    </>
                ) : (
                    <>
                        <div className="w-20 h-20 rounded-full bg-primary/20flex items-center justify-center group-hover:scale-110 transition-transform pulse-slow">
                            <Upload className="w-10 h-10 text-primary" />
                        </div>
                        <div className="space-y-2">
                            <p className="text-lg font-semibold text-foreground">
                                Upload your image
                            </p>
                            <p className="text-sm text-muted-foreground">
                                Drag and drop or click to browse
                            </p>
                            <p className="text-xs text-muted-foreground">
                                Supports JPG, PNG, WEBP
                            </p>
                        </div>
                    </>
                )}
            </div>
        </div>
    );
}
