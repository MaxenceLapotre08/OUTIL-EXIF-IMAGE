'use client';

import { useState } from 'react';
import { ImageUploader } from '@/components/ImageUploader';
import { AddressInput } from '@/components/AddressInput';
import { FormatSelector } from '@/components/FormatSelector';
import { ImagePreview } from '@/components/ImagePreview';
import { Download, Sparkles, Loader2, CheckCircle } from 'lucide-react';
import { api } from '@/lib/api';

export default function Home() {
  const [selectedImage, setSelectedImage] = useState<File | null>(null);
  const [address, setAddress] = useState('');
  const [format, setFormat] = useState<'jpeg' | 'png' | 'webp'>('jpeg');
  const [isProcessing, setIsProcessing] = useState(false);
  const [processedBlob, setProcessedBlob] = useState<Blob | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const handleProcess = async () => {
    if (!selectedImage || !address.trim()) {
      setError('Please select an image and enter an address');
      return;
    }

    setIsProcessing(true);
    setError(null);
    setSuccess(false);
    setProcessedBlob(null);

    try {
      const blob = await api.processImage({
        file: selectedImage,
        address,
        format,
      });

      setProcessedBlob(blob);
      setSuccess(true);

      // Auto-download
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${selectedImage.name.split('.')[0]}_gps.${format}`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to process image. Please try again.');
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="min-h-screen gradient-animated">
      {/* Header */}
      <header className="glass border-b border-border/50 backdrop-blur-lg sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg gradient-primary flex items-center justify-center">
              <Sparkles className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-foreground">EXIF Metadata Editor</h1>
              <p className="text-sm text-muted-foreground">Add geolocation to your images</p>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Left Column - Upload & Preview */}
          <div className="space-y-6">
            <div className="glass rounded-2xl p-6 hover-lift">
              <h2 className="text-xl font-semibold text-foreground mb-4">Upload Image</h2>
              <ImageUploader
                onImageSelected={setSelectedImage}
                selectedImage={selectedImage}
              />
            </div>

            {selectedImage && (
              <div className="glass rounded-2xl p-6 hover-lift">
                <ImagePreview file={selectedImage} />
              </div>
            )}
          </div>

          {/* Right Column - Settings & Action */}
          <div className="space-y-6">
            <div className="glass rounded-2xl p-6 hover-lift">
              <h2 className="text-xl font-semibold text-foreground mb-6">Settings</h2>
              <div className="space-y-6">
                <AddressInput value={address} onChange={setAddress} />
                <FormatSelector value={format} onChange={setFormat} />
              </div>
            </div>

            {/* Process Button */}
            <div className="glass rounded-2xl p-6">
              <button
                onClick={handleProcess}
                disabled={!selectedImage || !address.trim() || isProcessing}
                className={`
                  w-full py-4 px-6 rounded-xl font-semibold text-lg transition-all
                  flex items-center justify-center gap-3
                  ${!selectedImage || !address.trim() || isProcessing
                    ? 'bg-muted text-muted-foreground cursor-not-allowed'
                    : 'gradient-primary text-white hover:shadow-2xl hover:scale-105 hover-lift'
                  }
                `}
              >
                {isProcessing ? (
                  <>
                    <Loader2 className="w-6 h-6 animate-spin" />
                    Processing...
                  </>
                ) : success ? (
                  <>
                    <CheckCircle className="w-6 h-6" />
                    Downloaded!
                  </>
                ) : (
                  <>
                    <Download className="w-6 h-6" />
                    Generate & Download
                  </>
                )}
              </button>

              {error && (
                <div className="mt-4 p-4 rounded-lg bg-destructive/20 border border-destructive/50">
                  <p className="text-sm text-red-400">{error}</p>
                </div>
              )}

              {success && !error && (
                <div className="mt-4 p-4 rounded-lg bg-green-500/20 border border-green-500/50">
                  <p className="text-sm text-green-400 font-medium">
                    ✓ Image processed successfully! Download started automatically.
                  </p>
                </div>
              )}
            </div>

            {/* Info Box */}
            <div className="glass rounded-2xl p-6">
              <h3 className="font-semibold text-foreground mb-3">How it works</h3>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li className="flex items-start gap-2">
                  <span className="text-primary mt-1">•</span>
                  <span>Upload your image (JPG, PNG, or WEBP)</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-primary mt-1">•</span>
                  <span>Enter a target address for geolocation</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-primary mt-1">•</span>
                  <span>Choose your preferred output format</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-primary mt-1">•</span>
                  <span>Click to process and download</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="glass border-t border-border/50 mt-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <p className="text-center text-sm text-muted-foreground">
            Built with Next.js 14, FastAPI & Python • Secure & Privacy-focused
          </p>
        </div>
      </footer>
    </div>
  );
}
