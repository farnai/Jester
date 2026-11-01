import React, { useEffect, useRef, useState } from 'react';

interface ShareCardModalProps {
  isOpen: boolean;
  onClose: () => void;
  layer: { number: number; title: string; subtitle?: string } | null;
  item: { id: string; label: string; text: string; sign_badge?: string } | null;
}

export const ShareCardModal: React.FC<ShareCardModalProps> = ({
  isOpen,
  onClose,
  layer,
  item,
}) => {
  const [isGenerating, setIsGenerating] = useState(false);
  const [downloadSuccess, setDownloadSuccess] = useState(false);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  // Close on Escape
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    if (isOpen) {
      window.addEventListener('keydown', handleKeyDown);
    }
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen || !layer || !item) return null;

  // Helper to wrap text into lines on canvas
  const wrapText = (
    ctx: CanvasRenderingContext2D,
    text: string,
    x: number,
    y: number,
    maxWidth: number,
    lineHeight: number
  ) => {
    const words = text.split(' ');
    let line = '';
    let currentY = y;

    for (let n = 0; n < words.length; n++) {
      const testLine = line + words[n] + ' ';
      const metrics = ctx.measureText(testLine);
      const testWidth = metrics.width;
      if (testWidth > maxWidth && n > 0) {
        ctx.fillText(line.trim(), x, currentY);
        line = words[n] + ' ';
        currentY += lineHeight;
      } else {
        line = testLine;
      }
    }
    ctx.fillText(line.trim(), x, currentY);
    return currentY;
  };

  // Helper to generate Canvas Blob
  const generateBlob = async (): Promise<Blob | null> => {
    const canvas = canvasRef.current || document.createElement('canvas');
    canvas.width = 1080;
    canvas.height = 1080;
    const ctx = canvas.getContext('2d');
    if (!ctx) return null;

    // Background Warm Canvas
    ctx.fillStyle = '#FAF7F2';
    ctx.fillRect(0, 0, 1080, 1080);

    // Subtle Brand Top Accent Bar
    ctx.fillStyle = '#FF7A2F';
    ctx.fillRect(0, 0, 1080, 16);

    // White Inner Card
    const cardX = 80;
    const cardY = 120;
    const cardW = 920;
    const cardH = 840;
    const radius = 32;

    ctx.fillStyle = '#FFFFFF';
    ctx.strokeStyle = '#E6E0D7';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.roundRect(cardX, cardY, cardW, cardH, radius);
    ctx.fill();
    ctx.stroke();

    // JESTER Branding Header
    ctx.fillStyle = '#FF7A2F';
    ctx.font = 'bold 36px "Noto Sans Georgian", sans-serif';
    ctx.fillText('J E S T E R', cardX + 60, cardY + 90);

    ctx.fillStyle = '#788292';
    ctx.font = '600 20px "Noto Sans Georgian", sans-serif';
    ctx.fillText('RELATIONSHIP INTELLIGENCE', cardX + 60, cardY + 125);

    // Divider Line
    ctx.strokeStyle = '#F0EBE3';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(cardX + 60, cardY + 155);
    ctx.lineTo(cardX + cardW - 60, cardY + 155);
    ctx.stroke();

    // Layer Badge / Subtitle
    ctx.fillStyle = '#FF7A2F';
    ctx.font = 'bold 22px "Noto Sans Georgian", sans-serif';
    ctx.fillText(`შრე ${layer.number} • ${layer.title.toUpperCase()}`, cardX + 60, cardY + 210);

    // Item Label & Sign Badge
    ctx.fillStyle = '#222630';
    ctx.font = 'bold 34px "Noto Sans Georgian", sans-serif';
    const labelText = item.sign_badge ? `${item.label}  ( ${item.sign_badge} )` : item.label;
    ctx.fillText(labelText, cardX + 60, cardY + 270);

    // Quote Container Box
    ctx.fillStyle = '#FFFBF7';
    ctx.strokeStyle = '#FED7AA';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.roundRect(cardX + 60, cardY + 310, cardW - 120, 380, 20);
    ctx.fill();
    ctx.stroke();

    // Orange left border accent on quote
    ctx.fillStyle = '#FF7A2F';
    ctx.beginPath();
    ctx.roundRect(cardX + 60, cardY + 310, 8, 380, [20, 0, 0, 20]);
    ctx.fill();

    // Interpretation Quote Text
    ctx.fillStyle = '#272C36';
    ctx.font = 'italic 500 28px "Noto Sans Georgian", sans-serif';
    wrapText(ctx, `„${item.text}“`, cardX + 100, cardY + 380, cardW - 200, 48);

    // Privacy Notice & Watermark inside card
    ctx.fillStyle = '#8C94A0';
    ctx.font = '500 18px "Noto Sans Georgian", sans-serif';
    ctx.fillText('ასტრონომიულად დამოწმებული პირადი ინტერპრეტაცია', cardX + 60, cardY + 740);

    ctx.fillStyle = '#FF7A2F';
    ctx.font = 'bold 22px "Noto Sans Georgian", sans-serif';
    ctx.fillText('jester.ge', cardX + cardW - 180, cardY + 740);

    return new Promise((resolve) => {
      canvas.toBlob((blob) => resolve(blob), 'image/png');
    });
  };

  const handleDownload = async () => {
    try {
      setIsGenerating(true);
      const blob = await generateBlob();
      if (!blob) return;

      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `jester-insight-${item.id}.png`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);

      setDownloadSuccess(true);
      setTimeout(() => setDownloadSuccess(false), 3000);
    } catch (err) {
      console.error('Download failed:', err);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleShare = async () => {
    try {
      setIsGenerating(true);
      const blob = await generateBlob();
      if (!blob) return;

      const file = new File([blob], `jester-insight-${item.id}.png`, { type: 'image/png' });

      if (navigator.canShare && navigator.canShare({ files: [file] })) {
        await navigator.share({
          title: `JESTER — ${layer.title}`,
          text: `„${item.text}“\n— JESTER (${item.label})`,
          files: [file],
        });
      } else {
        // Fallback to download if Web Share file sharing is not supported
        await handleDownload();
      }
    } catch (err) {
      if ((err as Error)?.name !== 'AbortError') {
        console.error('Share failed, falling back to download:', err);
        await handleDownload();
      }
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="home-modal-overlay" role="dialog" aria-modal="true" aria-labelledby="share-modal-title">
      <div className="home-modal-backdrop" onClick={onClose} />
      <div className="home-modal-card">
        <div className="home-modal-header">
          <div>
            <h3 id="share-modal-title" className="home-modal-title">ბარათის გაზიარება</h3>
            <p className="home-modal-subtitle">
              შენი პირადი ინტერპრეტაციის დაცული ბარათი (PNG)
            </p>
          </div>
          <button type="button" className="home-modal-close-btn" onClick={onClose} aria-label="დახურვა">
            ✕
          </button>
        </div>

        {/* Live Card Preview */}
        <div className="home-share-preview-card">
          <div className="home-share-preview-brand">
            <span className="home-share-preview-logo">J E S T E R</span>
            <span className="home-share-preview-slogan">Relationship Intelligence</span>
          </div>

          <div className="home-share-preview-meta">
            <span className="home-share-preview-layer">შრე {layer.number} • {layer.title}</span>
            <div className="home-share-preview-title-row">
              <h4 className="home-share-preview-label">{item.label}</h4>
              {item.sign_badge && (
                <span className="home-share-preview-badge">{item.sign_badge}</span>
              )}
            </div>
          </div>

          <blockquote className="home-share-preview-quote">
            „{item.text}“
          </blockquote>

          <div className="home-share-preview-footer">
            <span className="home-share-preview-safe">✓ პირადი ასტროლოგიური მონაცემები 100% დაცულია</span>
            <span className="home-share-preview-url">jester.ge</span>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="home-modal-actions">
          <button
            type="button"
            className="home-btn home-btn-primary"
            onClick={handleShare}
            disabled={isGenerating}
          >
            {isGenerating ? 'მზადდება…' : 'გაზიარება ↗'}
          </button>
          <button
            type="button"
            className="home-btn home-btn-outline"
            onClick={handleDownload}
            disabled={isGenerating}
          >
            {downloadSuccess ? 'სურათი შენახულია ✓' : 'სურათის შენახვა (PNG) ⎘'}
          </button>
          <button
            type="button"
            className="home-btn home-btn-ghost"
            onClick={onClose}
          >
            დახურვა
          </button>
        </div>
      </div>
    </div>
  );
};

