'use client'

import { motion } from 'framer-motion'

export function AuthCard({ children }: { children: React.ReactNode }) {
    return (
        <motion.div
            initial={{ opacity: 0, y: 20, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            transition={{ duration: 0.5, ease: 'easeOut' }}
            className="
        w-full max-w-md
        rounded-2xl
        border border-white/10
        bg-white/5
        backdrop-blur
        p-8
      "
        >
            {children}
        </motion.div>
    )
}
