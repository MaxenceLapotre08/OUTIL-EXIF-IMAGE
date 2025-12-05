'use client';

import { useState } from 'react';
import { MapPin, Loader2 } from 'lucide-react';
import { api } from '@/lib/api';

interface AddressInputProps {
    value: string;
    onChange: (value: string) => void;
    onCoordinatesFound?: (lat: number, lon: number) => void;
}

export function AddressInput({ value, onChange, onCoordinatesFound }: AddressInputProps) {
    const [isValidating, setIsValidating] = useState(false);
    const [coordinates, setCoordinates] = useState<{ lat: number; lon: number } | null>(null);
    const [error, setError] = useState<string | null>(null);

    const handleBlur = async () => {
        if (!value.trim()) {
            setCoordinates(null);
            setError(null);
            return;
        }

        setIsValidating(true);
        setError(null);

        try {
            const result = await api.getCoordinates(value);
            setCoordinates({ lat: result.latitude, lon: result.longitude });
            onCoordinatesFound?.(result.latitude, result.longitude);
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Could not find this address');
            setCoordinates(null);
        } finally {
            setIsValidating(false);
        }
    };

    return (
        <div className="space-y-2">
            <label className="text-sm font-medium text-foreground flex items-center gap-2">
                <MapPin className="w-4 h-4 text-primary" />
                Target Address
            </label>
            <div className="relative">
                <input
                    type="text"
                    value={value}
                    onChange={(e) => onChange(e.target.value)}
                    onBlur={handleBlur}
                    placeholder="Enter address (e.g., Eiffel Tower, Paris)"
                    className="w-full px-4 py-3 rounded-lg bg-secondary/50 border border-border text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary transition-all"
                />
                {isValidating && (
                    <div className="absolute right-3 top-1/2 -translate-y-1/2">
                        <Loader2 className="w-5 h-5 text-primary animate-spin" />
                    </div>
                )}
            </div>

            {coordinates && (
                <div className="glassp-3 rounded-lg text-xs space-y-1">
                    <p className="text-green-400 font-medium">✓ Address found</p>
                    <p className="text-muted-foreground">
                        Coordinates: {coordinates.lat.toFixed(6)}, {coordinates.lon.toFixed(6)}
                    </p>
                </div>
            )}

            {error && (
                <div className="glass p-3 rounded-lg text-xs">
                    <p className="text-red-400">✗ {error}</p>
                </div>
            )}
        </div>
    );
}
