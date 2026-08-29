function blogPostApp() {
    return {
        ...themeMixin(),
        post: null,
        loading: true,
        async init() {
            this.initTheme();
            const slug = window.location.pathname.split('/').filter(Boolean).pop();
            try {
                const res = await fetch('/api/blog/' + slug);
                if (res.ok) {
                    this.post = await res.json();
                }
            } catch (e) {
                console.error('Failed to load post', e);
            } finally {
                this.loading = false;
            }
        },
        get formattedUpdatedAt() {
            if (!this.post?.updated_at) return '';
            return new Date(this.post.updated_at).toLocaleDateString(undefined, {
                year: 'numeric',
                month: 'long',
                day: 'numeric',
            });
        }
    };
}