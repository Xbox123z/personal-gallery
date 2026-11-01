# 天狗线人 · 个人主页 Gallery

一站展示 [Xbox123z（天狗线人）](https://github.com/Xbox123z) 的全部作品：

- **GitHub**：全部公开仓库（可搜索、按语言筛选）＋私有仓库名单
- **Bilibili「千早爱圣音」**：投稿视频（站内内嵌播放）、视频直链 m3u8 索引、图文动态精选
- **谷歌博客**：xbox123z-github 的全部文章
- **社交**：Instagram、Facebook 入口与近期帖子

## 技术

纯静态页面（`index.html`）＋ Deno 静态服务（`main.ts`），部署于 Deno Deploy。
页面数据为构建时快照，由 `build.py` 从 GitHub API、Bilibili 空间页与 Blogger feed 汇总生成；
B 站视频直链带时效签名，过期后内嵌播放器不受影响。

## 本地构建

```bash
python3 build.py   # 重新生成 index.html 与 index.m3u8（需先备好数据文件）
deno task start    # 本地预览
```
