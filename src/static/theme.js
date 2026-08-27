/**
 * Shared theme handling, spread into any Alpine component's x-data.
 *
 * Usage:
 *   <body x-data="{ ...themeMixin(), other: 'state' }" x-init="initTheme()">
 *
 * Or inside a named component (like editor()):
 *   function editor() {
 *     return {
 *       ...themeMixin(),
 *       ...otherState,
 *       init() { this.initTheme(); },
 *     };
 *   }
 *
 * initTheme() must be called explicitly from the component's own init/x-init,
 * since Alpine only ever calls one `init()` per component and we don't want
 * to silently overwrite a component's own init logic by spreading one in.
 */
function themeMixin() {
    return {
        theme: localStorage.getItem('theme')
            || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'),

        initTheme() {
            document.documentElement.setAttribute('data-theme', this.theme);

            this.$watch('theme', (value) => {
                localStorage.setItem('theme', value);
                document.documentElement.setAttribute('data-theme', value);
            });

            // Keep in sync if the theme is changed in another tab
            window.addEventListener('storage', (e) => {
                if (e.key === 'theme' && e.newValue) {
                    this.theme = e.newValue;
                }
            });
        },

        toggleTheme() {
            this.theme = this.theme === 'dark' ? 'light' : 'dark';
        },
    };
}
