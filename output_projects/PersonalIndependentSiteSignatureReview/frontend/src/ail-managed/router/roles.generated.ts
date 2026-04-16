export const roleRequired: Record<string, string> = {
};

export type NavPage = {
  path: string;
  label: string;
  public?: boolean;
  requiresAuth?: boolean;
  role?: string;
};

export const navPages: NavPage[] = [
  { path: "/403", label: "Forbidden", public: true },
];
