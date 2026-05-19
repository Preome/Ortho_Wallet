import './globals.css';
import { Toaster } from 'react-hot-toast';

export const metadata = {
  title: 'Ortho Wallet',
  description: 'Digital Wallet for Orthodontic Payments',
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        {children}
        <Toaster position="top-right" />
      </body>
    </html>
  );
}