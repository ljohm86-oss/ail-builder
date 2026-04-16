export interface Product {
  id: string;
  title: string;
  price: number;
  rating: number;
  reviews: number;
  image: string;
  isPrime: boolean;
  category: string;
}

export const products: Product[] = [
  {
    id: "1",
    title: "Sony WH-1000XM5 Wireless Noise Canceling Headphones, 30 Hours Battery Life, Over Ear Headphones with Auto Noise Canceling Optimizer, Carry Case, Hands-Free Calling, Alexa Voice Control, Black",
    price: 348.00,
    rating: 4.5,
    reviews: 12453,
    image: "https://m.media-amazon.com/images/I/51SKmu2G9FL._AC_SL1000_.jpg",
    isPrime: true,
    category: "Electronics"
  },
  {
    id: "2",
    title: "Apple 2024 MacBook Air 13-inch Laptop with M3 chip: 13.6-inch Liquid Retina Display, 8GB Unified Memory, 256GB SSD Storage, Backlit Keyboard, 1080p FaceTime HD Camera, Touch ID; Midnight",
    price: 1099.00,
    rating: 4.8,
    reviews: 892,
    image: "https://m.media-amazon.com/images/I/71S4sIPFvBL._AC_SL1500_.jpg",
    isPrime: true,
    category: "Electronics"
  },
  {
    id: "3",
    title: "Atomic Habits: An Easy & Proven Way to Build Good Habits & Break Bad Ones",
    price: 13.79,
    rating: 4.8,
    reviews: 120453,
    image: "https://m.media-amazon.com/images/I/81YkqyaFVEL._SL1500_.jpg",
    isPrime: true,
    category: "Books"
  },
  {
    id: "4",
    title: "Instant Pot Duo 7-in-1 Electric Pressure Cooker, Slow Cooker, Rice Cooker, Steamer, Sauté, Yogurt Maker, Warmer & Sterilizer, Includes App With Over 800 Recipes, Stainless Steel, 6 Quart",
    price: 99.95,
    rating: 4.7,
    reviews: 156789,
    image: "https://m.media-amazon.com/images/I/71WtwEvYDOS._AC_SL1500_.jpg",
    isPrime: false,
    category: "Home & Kitchen"
  },
  {
    id: "5",
    title: "Logitech MX Master 3S - Wireless Performance Mouse, Ergo, 8K DPI, Track on Glass, Quiet Clicks, USB-C, Bluetooth, Windows, Linux, Chrome - Graphite",
    price: 99.99,
    rating: 4.7,
    reviews: 14521,
    image: "https://m.media-amazon.com/images/I/61ni3t1ryQL._AC_SL1500_.jpg",
    isPrime: true,
    category: "Electronics"
  },
  {
    id: "6",
    title: "Samsung 990 PRO SSD 2TB PCIe 4.0 M.2 2280 Internal Solid State Hard Drive, Seq. Read Speeds Up to 7,450 MB/s for High End Gaming, Video Editing, 3D Modeling, MZ-V9P2T0B/AM",
    price: 169.99,
    rating: 4.8,
    reviews: 10234,
    image: "https://m.media-amazon.com/images/I/811PrFd9L0L._AC_SL1500_.jpg",
    isPrime: true,
    category: "Electronics"
  },
  {
    id: "7",
    title: "Keurig K-Classic Coffee Maker, Single Serve K-Cup Pod Coffee Brewer, 6 to 10 Oz. Brew Sizes, Black",
    price: 79.99,
    rating: 4.6,
    reviews: 98765,
    image: "https://m.media-amazon.com/images/I/71R32RjG32L._AC_SL1500_.jpg",
    isPrime: true,
    category: "Home & Kitchen"
  },
  {
    id: "8",
    title: "LEGO Star Wars: The Mandalorian The Child 75318 Building Kit; Collectible Build-and-Display Model for Ages 10+, New 2021 (1,073 Pieces)",
    price: 71.99,
    rating: 4.9,
    reviews: 23456,
    image: "https://m.media-amazon.com/images/I/81wF89V5HCL._AC_SL1500_.jpg",
    isPrime: true,
    category: "Toys & Games"
  }
];
