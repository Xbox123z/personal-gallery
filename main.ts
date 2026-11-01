// Personal gallery static server for Deno Deploy.
// Serves index.html at / and index.m3u8 with the proper HLS content type.
import { serveDir } from "jsr:@std/http/file-server";

Deno.serve((req) => {
  const url = new URL(req.url);
  if (url.pathname === "/index.m3u8" || url.pathname === "/bilibili.m3u8") {
    return Deno.readTextFile("./index.m3u8").then(
      (text) =>
        new Response(text, {
          headers: {
            "content-type": "application/vnd.apple.mpegurl; charset=utf-8",
            "access-control-allow-origin": "*",
            "cache-control": "public, max-age=300",
          },
        }),
      () => new Response("not found", { status: 404 }),
    );
  }
  return serveDir(req, { fsRoot: ".", showDirListing: false, quiet: true });
});
