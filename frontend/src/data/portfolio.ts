export const CONTACT = {
  phone: '+91 8840872713',
  email: 'tusharchowdhury6611@gmail.com',
  location: 'Bengaluru, Karnataka, India',
} as const

export const RESUME_URL =
  'https://1drv.ms/b/c/5bc38c510559f1a0/IQD5JrcQRFbnRb_3Vd9PaZulAUQZ3eijzmblXAfNAvcKBSk?e=Mbqpdz'

export const stats = [
  { value: '9', label: 'Years Experience' },
  { value: '10+', label: 'Projects Delivered' },
  { value: 'AI/ML', label: 'Production Systems' },
  { value: 'Azure + AWS', label: 'Cloud Native' },
] as const

export type SkillGroup = { title: string; items: string[] }

export const skillGroups: SkillGroup[] = [
  {
    title: 'Languages',
    items: ['Python', 'C#', 'JavaScript / TypeScript', 'SQL'],
  },
  {
    title: 'Frameworks',
    items: ['.NET Core', 'FastAPI', 'Flask', 'React / Next.js'],
  },
  {
    title: 'AI & Machine Learning',
    items: ['TensorFlow', 'PyTorch', 'Scikit-learn', 'Keras • Pandas • NumPy'],
  },
  {
    title: 'Cloud & DevOps',
    items: ['Azure • AWS', 'Azure DevOps', 'Docker • Kubernetes', 'CI / CD Pipelines'],
  },
  {
    title: 'Microservices & Architecture',
    items: [
      'Distributed Systems',
      'Event-Driven Architecture',
      'API Gateway',
      'Messaging Queues & Topics',
    ],
  },
  {
    title: 'Databases',
    items: ['PostgreSQL • SQL Server', 'MongoDB • Redis', 'Cosmos DB', 'Query Optimization'],
  },
]
