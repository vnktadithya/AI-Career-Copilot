import Link from 'next/link'

export function AuthFooter({
    text,
    linkText,
    href,
}: {
    text: string
    linkText: string
    href: string
}) {
    return (
        <p className="text-sm text-zinc-400 text-center mt-6">
            {text}{' '}
            <Link href={href} className="text-white hover:underline">
                {linkText}
            </Link>
        </p>
    )
}
