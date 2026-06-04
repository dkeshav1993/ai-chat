// Curated hotel and room images from Unsplash (stable, public CDN)
const HOTEL_IMAGES = [
  'https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800&h=500&fit=crop&auto=format&q=80',
  'https://images.unsplash.com/photo-1582719508461-905c673771fd?w=800&h=500&fit=crop&auto=format&q=80',
  'https://images.unsplash.com/photo-1564501049412-61d2ad2d7732?w=800&h=500&fit=crop&auto=format&q=80',
  'https://images.unsplash.com/photo-1571003123894-1f0594d2b5d9?w=800&h=500&fit=crop&auto=format&q=80',
  'https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?w=800&h=500&fit=crop&auto=format&q=80',
  'https://images.unsplash.com/photo-1549294413-26f195200c16?w=800&h=500&fit=crop&auto=format&q=80',
  'https://images.unsplash.com/photo-1445019980597-93fa8acb246c?w=800&h=500&fit=crop&auto=format&q=80',
  'https://images.unsplash.com/photo-1551882547-ff40c63fe5fa?w=800&h=500&fit=crop&auto=format&q=80',
  'https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?w=800&h=500&fit=crop&auto=format&q=80',
  'https://images.unsplash.com/photo-1615460549969-36fa19521a4f?w=800&h=500&fit=crop&auto=format&q=80',
]

const ROOM_IMAGES = [
  'https://images.unsplash.com/photo-1631049307264-da0ec9d70304?w=700&h=450&fit=crop&auto=format&q=80',
  'https://images.unsplash.com/photo-1631049552057-403cdb8f0658?w=700&h=450&fit=crop&auto=format&q=80',
  'https://images.unsplash.com/photo-1611892440504-42a792e24d32?w=700&h=450&fit=crop&auto=format&q=80',
  'https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?w=700&h=450&fit=crop&auto=format&q=80',
  'https://images.unsplash.com/photo-1540518614846-7eded433c457?w=700&h=450&fit=crop&auto=format&q=80',
  'https://images.unsplash.com/photo-1522771739844-6a9f6d5f14af?w=700&h=450&fit=crop&auto=format&q=80',
]

function hashString(str: string): number {
  return Math.abs(
    str.split('').reduce((acc, c) => ((acc << 5) - acc + c.charCodeAt(0)) | 0, 0)
  )
}

export function getHotelImageUrl(hotelId: string, fallbackIndex = 0): string {
  const idx = hotelId ? hashString(hotelId) : fallbackIndex
  return HOTEL_IMAGES[idx % HOTEL_IMAGES.length]
}

export function getRoomImageUrl(seed: string, fallbackIndex = 0): string {
  const idx = seed ? hashString(seed) : fallbackIndex
  return ROOM_IMAGES[idx % ROOM_IMAGES.length]
}

/** Image error handler — swap broken src to fallback */
export function onImageError(event: Event, fallbackUrl: string): void {
  const img = event.target as HTMLImageElement
  if (img.src !== fallbackUrl) {
    img.src = fallbackUrl
  }
}

/**
 * Extract the first real image URL from the API images field.
 * The API returns images in two shapes:
 *  - Search results: Array<{links: [{size, providerHref, href}], ...}>
 *  - Hotel details:  { isDummy: bool, data: Array<{links: [...], ...}> }
 * Returns an empty string if no URL is found.
 */
export function extractFirstImageUrl(imagesField: unknown): string {
  let items: unknown[] = []
  if (Array.isArray(imagesField)) {
    items = imagesField
  } else if (imagesField && typeof imagesField === 'object') {
    const block = imagesField as Record<string, unknown>
    if (Array.isArray(block.data)) items = block.data
  }
  for (const item of items) {
    const img = item as Record<string, unknown>
    const links = Array.isArray(img.links) ? (img.links as Record<string, string>[]) : []
    for (const link of links) {
      const url = link.providerHref || link.href || ''
      if (url && url.trim()) return url.trim()
    }
  }
  return ''
}
