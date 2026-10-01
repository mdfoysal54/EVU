export const config = {
  appName: process.env.NEXT_PUBLIC_APP_NAME || "EVU",
  apiUrl: (process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000").replace(/\/$/, ""),
  apiPrefix: process.env.NEXT_PUBLIC_API_PREFIX || "/api/v1",
};
