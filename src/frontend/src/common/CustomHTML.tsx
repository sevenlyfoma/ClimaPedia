import DOMPurify from "dompurify";
import { ReactNode } from "react";

// Component which renders custom HTML safely
export function customHTML(html: string): ReactNode {
  const cleanHtml = DOMPurify.sanitize(html);
  return <div dangerouslySetInnerHTML={{ __html: cleanHtml }} />;
}
