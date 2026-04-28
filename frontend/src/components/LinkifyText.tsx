import { Fragment } from 'react'

export function LinkifyText({ text }: { text: string }) {
  const segments = text.split(/(https?:\/\/[^\s]+)/g)
  return segments.map((segment, i) => {
    if (/^https?:\/\//.test(segment)) {
      return (
        <a
          key={i}
          href={segment}
          target="_blank"
          rel="noopener noreferrer"
          className="underline hover:text-pink-300"
        >
          {segment}
        </a>
      )
    }
    const lines = segment.split('\n')
    return (
      <Fragment key={i}>
        {lines.map((line, j) => (
          <Fragment key={j}>
            {j > 0 ? <br /> : null}
            {line}
          </Fragment>
        ))}
      </Fragment>
    )
  })
}
