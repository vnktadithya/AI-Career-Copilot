'use client'

import Link from 'next/link'
import { ArrowRight } from 'lucide-react'
import { motion } from 'framer-motion'

export default function LandingPage() {
  return (
    <main className="h-screen w-screen overflow-hidden bg-black text-white relative">

      {/* Background Gradient */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 1.2 }}
        className="absolute inset-0 bg-gradient-to-br from-indigo-600/20 via-transparent to-purple-600/20 blur-3xl"
      />

      {/* Navbar */}
      <motion.nav
        initial={{ y: -20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 0.2, duration: 0.6 }}
        className="relative z-10 flex items-center justify-between px-8 py-6 max-w-7xl mx-auto"
      >
        <h1 className="text-xl font-semibold tracking-wide">
          AI Powered Career Copilot
        </h1>
      </motion.nav>

      {/* Main Content Grid */}
      <div className="relative z-10 h-[calc(100vh-80px)] max-w-7xl mx-auto grid grid-rows-[1fr_auto] px-6">

        {/* Hero */}
        <motion.section
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4, duration: 0.8, ease: 'easeOut' }}
          className="flex flex-col items-center justify-center text-center"
        >
          <h2 className="text-5xl md:text-6xl font-bold leading-tight tracking-tight">
            Build Your Career Story <br />
            <span className="bg-gradient-to-r from-indigo-400 to-purple-400 bg-clip-text text-transparent">
              Automatically with AI
            </span>
          </h2>

          <p className="mt-5 text-lg text-gray-300 max-w-2xl">
            Transform GitHub activity into professional narratives for
            LinkedIn, portfolios, and resumes — with full human control.
          </p>

          <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ delay: 0.8, duration: 0.4 }}
          >
            <Link
              href="/auth/login"
              className="mt-8 inline-flex items-center gap-2 px-8 py-4 rounded-xl bg-white text-black font-semibold text-lg hover:bg-gray-200 transition"
            >
              Get Started
              <ArrowRight size={20} />
            </Link>
          </motion.div>
        </motion.section>

        {/* Features */}
        <motion.section
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1, duration: 0.6 }}
          className="grid grid-cols-1 md:grid-cols-3 gap-6 pb-10"
        >
          {[
            {
              title: 'GitHub-Aware Intelligence',
              desc: 'Understands real repositories, commits, and diffs.'
            },
            {
              title: 'Human-in-the-Loop',
              desc: 'Nothing happens without your explicit approval.'
            },
            {
              title: 'Always In Context',
              desc: 'Your career story stays consistent across time.'
            }
          ].map((feature, index) => (
            <motion.div
              key={index}
              whileHover={{ y: -4 }}
              transition={{ type: 'spring', stiffness: 200 }}
              className="rounded-2xl border border-white/10 p-5 bg-white/5 backdrop-blur"
            >
              <h3 className="text-lg font-semibold mb-2">
                {feature.title}
              </h3>
              <p className="text-sm text-gray-400">
                {feature.desc}
              </p>
            </motion.div>
          ))}
        </motion.section>

      </div>

      {/* Footer */}
      <motion.footer
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1.3 }}
        className="absolute bottom-4 w-full text-center text-xs text-gray-500"
      >
        © {new Date().getFullYear()} AI Powered Career Copilot. Built for developers
      </motion.footer>

    </main>
  )
}
