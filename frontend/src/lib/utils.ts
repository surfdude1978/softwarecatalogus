import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

/**
 * Utility voor het combineren van Tailwind classes (shadcn/ui patroon).
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
