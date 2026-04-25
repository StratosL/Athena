# Plan: Mobile "More" Bottom Sheet for Guide & Settings

## Context

On mobile, Guide and Settings pages are unreachable. The desktop `Sidebar` renders them as `bottomItems`, but the mobile `BottomNav` only receives the 6 main nav items — `bottomItemsWithActive` is never passed to it. The bottom nav already has 6 items with horizontal scroll, and adding 2 more would bury them off-screen.

**Solution**: Replace the current 6-item scrollable bottom nav with **5 direct tabs + a "More" button** that opens a bottom sheet containing the overflow items.

**Tab layout**:
- Direct tabs: **Dashboard, Tasks, Daily Plan, Athena, More**
- More sheet: **Pomodoro, Analytics, Guide, Settings**

## Files to Modify (4 files, 0 new files)

### 1. `frontend/src/pages-new/layout/navItems.ts`

Restructure exports into two arrays:

- `primaryNavItems` (5 items): Dashboard, Tasks, Daily Plan, Athena — these show as direct tabs
- `overflowNavItems` (4 items): Pomodoro, Analytics, Guide, Settings — these go in the "More" sheet

Keep existing `navItems` and `bottomNavItems` exports for the desktop Sidebar (unchanged).

### 2. `frontend/src/design-system/components/layout/BottomNav/BottomNav.types.ts`

Add `overflowItems?: SidebarNavItem[]` to `BottomNavProps`.

### 3. `frontend/src/design-system/components/layout/BottomNav/index.tsx`

Add the "More" button and bottom sheet:

- Import `useState` from React, `AnimatePresence` + `motion` from `motion/react`, `MoreHorizontal` from lucide, `glassmorphismClasses` from design system
- Add local `isMoreOpen` state
- Render the 5 primary items as-is (existing `items` prop)
- After the items loop, render a "More" button styled identically to nav items (same `min-w-[64px] flex-1` layout) with `MoreHorizontal` icon
- Highlight the "More" button with `text-luxury-gold` if any overflow item is active
- Bottom sheet uses ChatSidebar's animation pattern adapted for bottom entry:
  - Backdrop: `motion.div` with `bg-black/50 backdrop-blur-sm`, click-to-close, `z-40`
  - Sheet: `motion.div` with `initial={{ y: "100%" }}`, `animate={{ y: 0 }}`, `exit={{ y: "100%" }}`, spring transition `damping: 25, stiffness: 300`, `z-50`
  - Sheet styling: `rounded-t-2xl`, glassmorphism classes, `pb-safe` for safe area
  - Drag handle bar at top (centered `w-10 h-1 rounded-full bg-luxury-text-secondary/30`)
  - List of overflow items as `<Link>` elements, each with icon + label, active state highlighting
  - Clicking a nav item closes the sheet
  - Position sheet above the bottom nav (`bottom-[calc(theme(spacing.16)+env(safe-area-inset-bottom))]` or simply `bottom-16`) so the nav bar stays visible underneath

### 4. `frontend/src/pages-new/layout/AppShell.tsx`

- Import `primaryNavItems` and `overflowNavItems` from `navItems.ts`
- Build `primaryWithActive` from `primaryNavItems` (same active logic)
- Build `overflowWithActive` from `overflowNavItems` (same active logic)
- Pass both to `<BottomNav items={primaryWithActive} overflowItems={overflowWithActive} />`
- Desktop `<Sidebar>` stays unchanged — still uses `navItems` + `bottomNavItems`

## Animation Pattern (reusing ChatSidebar)

```tsx
<AnimatePresence>
  {isMoreOpen && (
    <>
      <motion.div
        className="fixed inset-0 bg-black/50 backdrop-blur-sm z-40"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        onClick={() => setIsMoreOpen(false)}
      />
      <motion.div
        className="fixed bottom-16 left-0 right-0 z-50 rounded-t-2xl ..."
        initial={{ y: "100%" }}
        animate={{ y: 0 }}
        exit={{ y: "100%" }}
        transition={{ type: "spring", damping: 25, stiffness: 300 }}
      >
        {/* drag handle + overflow nav items */}
      </motion.div>
    </>
  )}
</AnimatePresence>
```

## What Does NOT Change

- Desktop sidebar — still shows all 6 main items + Guide/Settings at bottom
- Guide page, Settings page — no modifications
- Athena chat FAB — still hidden on `/athena`, shown on other pages
- No new dependencies or files

## Verification

1. `npx tsc --noEmit` — 0 TypeScript errors
2. `npx vite build` — successful build
3. Manual: on mobile viewport (375x667), confirm 5 tabs visible, "More" opens sheet with 4 items, tapping an item navigates and closes sheet, backdrop click closes sheet
4. Manual: on desktop (1280+), confirm sidebar unchanged with all items
5. Confirm "More" button highlights gold when on /pomodoro, /analytics, /guide, or /settings
