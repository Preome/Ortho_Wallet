import './globals.css'

export const metadata = {
  title: 'Ortho Wallet',
  description: 'Digital Wallet for Orthodontic Payments',
}

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}