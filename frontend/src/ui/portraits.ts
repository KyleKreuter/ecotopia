const PORTRAIT_FILENAMES: Record<string, string> = {
  'karl': 'karl',
  'sarah': 'sarah',
  'mia': 'mia',
  'oleg': 'oleg',
  'kerstin': 'kerstin',
  'bernd': 'bernd',
  'henning': 'henning',
  'lena': 'lena',
  'dr. yuki': 'yuki',
  'pavel': 'pavel',
};

export function getPortraitPath(name: string): string {
  const key = name.toLowerCase();
  const filename = PORTRAIT_FILENAMES[key] ?? key;
  return `/assets/character/${filename}.png`;
}
