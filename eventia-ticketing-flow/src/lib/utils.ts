import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

/**
 * Checks if a specified font is available on the user's system
 * @param fontName The font family name to check
 * @returns Promise resolving to true if font is available, false otherwise
 */
export async function isFontAvailable(fontName: string): Promise<boolean> {
  try {
    // Use the FontFace API to detect if a font is loaded
    return await document.fonts.ready.then(() => {
      // Test if font is available by measuring text with it
      const testString = "abcdefghijklmnopqrstuvwxyz0123456789";
      const testEl = document.createElement("span");
      testEl.style.position = "absolute";
      testEl.style.left = "-9999px";
      testEl.style.fontSize = "72px";
      testEl.style.fontFamily = `'${fontName}', 'sans-serif'`;
      testEl.innerHTML = testString;
      document.body.appendChild(testEl);
      
      const fallbackWidth = testEl.offsetWidth;
      
      // Now set the fontFamily to just the font we're testing
      testEl.style.fontFamily = `'${fontName}'`;
      const actualWidth = testEl.offsetWidth;
      
      document.body.removeChild(testEl);
      
      // If the widths are different, the font is likely loaded
      return fallbackWidth !== actualWidth;
    });
  } catch (err) {
    console.error("Error checking font availability:", err);
    return false;
  }
}

/**
 * Loads a fallback font if the specified font isn't available
 * @param preferredFont The preferred font to use
 * @param fallbackFont The fallback font to use if preferred font is unavailable
 * @returns The font that should be used
 */
export async function loadOptimalFont(
  preferredFont: string,
  fallbackFont: string = "system-ui"
): Promise<string> {
  try {
    const isAvailable = await isFontAvailable(preferredFont);
    return isAvailable ? preferredFont : fallbackFont;
  } catch (err) {
    console.error("Error loading optimal font:", err);
    return fallbackFont;
  }
}
