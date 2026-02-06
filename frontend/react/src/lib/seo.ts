export const siteConfig = {
  name: "{{cookiecutter.project_name}}",
  description: "{{cookiecutter.project_description}}",
  url: "https://{{cookiecutter.domain_name}}",
} as const

export function getPageTitle(pageTitle?: string): string {
  if (!pageTitle) return siteConfig.name
  return `${pageTitle} | ${siteConfig.name}`
}

export function getSeoMeta(options?: {
  title?: string
  description?: string
}) {
  const title = options?.title ? getPageTitle(options.title) : siteConfig.name
  const description = options?.description ?? siteConfig.description

  return [
    { title },
    { name: "description", content: description },
    { property: "og:title", content: title },
    { property: "og:description", content: description },
    { name: "twitter:title", content: title },
    { name: "twitter:description", content: description },
  ]
}
