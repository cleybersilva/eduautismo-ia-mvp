# EduAutismo IA Frontend

## Getting Started

To run the frontend application:

1. **Navigate to the frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm run dev
   ```

4. **Open your browser:**
   Visit http://localhost:5173

## Project Structure

```
src/
├── App.jsx              # Main application component
├── main.jsx             # Application entry point
├── assets/              # Static assets (images, icons)
├── components/          # Reusable UI components
├── pages/               # Page components
├── services/            # API service layer
├── store/               # State management (Zustand)
├── styles/              # Global styles and CSS utilities
└── utils/               # Utility functions
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint
- `npm run format` - Format code with Prettier

## Technologies Used

- React 18
- Vite (build tool)
- Tailwind CSS (styling)
- React Router (routing)
- Zustand (state management)
- React Hook Form (form handling)
- Zod (validation)
- Lucide React (icons)

## Login Page Features

The new login page includes:

1. **Responsive Design**
   - Mobile-optimized layout
   - Desktop dual-column layout
   - Adaptive illustrations

2. **Accessibility**
   - High contrast mode
   - Keyboard navigation
   - Screen reader support

3. **User Experience**
   - Password visibility toggle
   - "Remember me" option
   - Clear error messaging
   - Smooth animations

4. **Security**
   - Visual security indicators
   - Encrypted connection messaging

## Troubleshooting

If you encounter issues:

1. **'vite' is not recognized:**
   ```bash
   npx vite
   ```

2. **Permission errors:**
   Run terminal as administrator or use:
   ```bash
   npm install --no-optional
   ```

3. **Port conflicts:**
   ```bash
   npm run dev -- --port 3000
   ```

## Development Guidelines

- Follow existing code style
- Use Tailwind CSS for styling
- Maintain accessibility standards
- Write meaningful commit messages
- Test responsive behavior