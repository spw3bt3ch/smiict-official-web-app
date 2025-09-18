# SMIICT Institute Course Platform - CSS Documentation

This directory contains all the CSS files for the SMIICT Institute Course Platform, organized for maintainability and performance.

## File Structure

```
static/css/
├── main.css           # Core styles and base components
├── responsive.css     # Media queries and responsive design
├── components.css     # Reusable UI components
├── admin.css         # Admin panel specific styles
├── animations.css    # Animations and transitions
├── print.css         # Print-specific styles
└── README.md         # This documentation file
```

## CSS Architecture

### 1. Main CSS (`main.css`)
Contains the core styles including:
- CSS Reset and base styles
- Typography system
- Color variables
- Layout utilities
- Navigation styles
- Button components
- Form elements
- Card components
- Footer styles

### 2. Responsive CSS (`responsive.css`)
Handles all responsive design with mobile-first approach:
- **Mobile (≤575px)**: Single column layouts, stacked elements
- **Small (576px-767px)**: Two-column grids, compact navigation
- **Medium (768px-991px)**: Tablet-optimized layouts
- **Large (992px-1199px)**: Desktop layouts with 3-4 columns
- **Extra Large (≥1200px)**: Full desktop experience
- **Ultra Wide (≥1400px)**: Large screen optimizations

### 3. Components CSS (`components.css`)
Reusable component styles:
- Course cards with hover effects
- Application cards
- Message cards
- Payment method selection
- Form groups and validation
- Button variants
- Loading states
- Progress bars
- Badges and status indicators
- Tooltips
- Modal dialogs

### 4. Admin CSS (`admin.css`)
Admin panel specific styles:
- Sidebar navigation
- Dashboard layout
- Data tables
- Admin forms
- Statistics cards
- Status badges
- Admin-specific components

### 5. Animations CSS (`animations.css`)
Animation and transition effects:
- Fade animations (in, out, up, down, left, right)
- Slide animations
- Scale animations
- Rotate animations
- Bounce effects
- Pulse effects
- Shake and wobble
- Loading spinners
- Hover effects
- Page transitions
- Stagger animations

### 6. Print CSS (`print.css`)
Print-optimized styles:
- Clean print layout
- Hidden interactive elements
- Proper page breaks
- Print-friendly typography
- Optimized colors for printing

## CSS Classes Reference

### Layout Classes
```css
.container          /* Main container with max-width */
.hero              /* Hero section styling */
.course-grid       /* Course cards grid layout */
.stats-grid        /* Statistics cards grid */
.admin-layout      /* Admin panel layout */
```

### Component Classes
```css
.course-card       /* Course card component */
.application-card  /* Application card component */
.message-card      /* Message card component */
.payment-method    /* Payment method selection */
.btn               /* Button base class */
.btn-primary       /* Primary button variant */
.btn-secondary     /* Secondary button variant */
.form-group        /* Form field container */
.form-control      /* Form input styling */
```

### Utility Classes
```css
.text-center       /* Center align text */
.mb-0 to .mb-6     /* Margin bottom utilities */
.mt-0 to .mt-6     /* Margin top utilities */
.p-0 to .p-6       /* Padding utilities */
.fade-in           /* Fade in animation */
.hover-lift        /* Hover lift effect */
.loading           /* Loading state */
```

### Status Classes
```css
.status-badge.pending    /* Pending status */
.status-badge.approved   /* Approved status */
.status-badge.rejected   /* Rejected status */
.status-badge.paid       /* Paid status */
.status-badge.unpaid     /* Unpaid status */
```

## Responsive Breakpoints

| Breakpoint | Min Width | Description |
|------------|-----------|-------------|
| xs | 0px | Extra small devices (phones) |
| sm | 576px | Small devices (landscape phones) |
| md | 768px | Medium devices (tablets) |
| lg | 992px | Large devices (desktops) |
| xl | 1200px | Extra large devices (large desktops) |
| xxl | 1400px | Ultra wide screens |

## Color Palette

### Primary Colors
- **Blue**: #3b82f6 (Primary brand color)
- **Blue Dark**: #1e3a8a (Dark blue for headers)
- **Blue Light**: #dbeafe (Light blue backgrounds)

### Status Colors
- **Success**: #10b981 (Green for success states)
- **Warning**: #f59e0b (Yellow for warnings)
- **Danger**: #ef4444 (Red for errors/danger)
- **Info**: #3b82f6 (Blue for information)

### Neutral Colors
- **Gray 50**: #f9fafb (Light backgrounds)
- **Gray 100**: #f3f4f6 (Card backgrounds)
- **Gray 500**: #6b7280 (Secondary text)
- **Gray 900**: #111827 (Primary text)

## Typography

### Font Family
- **Primary**: Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif
- **Fallback**: System fonts for better performance

### Font Sizes
- **h1**: 2.5rem (40px)
- **h2**: 2rem (32px)
- **h3**: 1.5rem (24px)
- **h4**: 1.25rem (20px)
- **h5**: 1.125rem (18px)
- **h6**: 1rem (16px)
- **Body**: 1rem (16px)
- **Small**: 0.875rem (14px)

## Animation Guidelines

### Duration
- **Fast**: 0.1s - 0.3s (Hover effects, micro-interactions)
- **Normal**: 0.5s - 0.7s (Page transitions, component animations)
- **Slow**: 1s+ (Loading animations, complex transitions)

### Easing
- **ease-out**: Most common for UI animations
- **ease-in-out**: Smooth bidirectional animations
- **cubic-bezier**: Custom easing for specific effects

### Performance
- Use `transform` and `opacity` for smooth animations
- Avoid animating `width`, `height`, `top`, `left` properties
- Use `will-change` for elements that will be animated
- Respect `prefers-reduced-motion` for accessibility

## Accessibility Features

### Reduced Motion
```css
@media (prefers-reduced-motion: reduce) {
    /* Disable animations for users who prefer reduced motion */
}
```

### High Contrast
- Sufficient color contrast ratios (WCAG AA compliant)
- Focus indicators for keyboard navigation
- Clear visual hierarchy

### Screen Reader Support
- Semantic HTML structure
- Proper heading hierarchy
- Alt text for images
- ARIA labels where needed

## Browser Support

- **Modern Browsers**: Chrome 90+, Firefox 88+, Safari 14+, Edge 90+
- **CSS Grid**: Full support in all modern browsers
- **Flexbox**: Full support with fallbacks
- **CSS Custom Properties**: Supported with fallbacks
- **CSS Animations**: Supported with graceful degradation

## Performance Optimizations

### CSS Loading
- Critical CSS inlined in HTML
- Non-critical CSS loaded asynchronously
- CSS files minified in production
- Unused CSS purged in production builds

### Animation Performance
- Hardware acceleration with `transform3d()`
- `will-change` property for animated elements
- Debounced scroll and resize handlers
- Efficient selectors to avoid reflows

## Development Guidelines

### Naming Convention
- Use BEM methodology for component classes
- Use descriptive, semantic class names
- Avoid overly specific selectors
- Use utility classes for common patterns

### File Organization
- Keep related styles together
- Use comments to separate sections
- Maintain consistent indentation (2 spaces)
- Group properties logically (position, display, box model, typography, visual)

### Maintenance
- Regular code reviews
- Performance audits
- Accessibility testing
- Cross-browser testing
- Mobile device testing

## Future Enhancements

- CSS-in-JS integration
- Component-based CSS architecture
- Design system implementation
- Advanced animation library
- CSS custom properties for theming
- Container queries support
- CSS Grid subgrid support
