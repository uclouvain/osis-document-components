/*
 *
 * OSIS stands for Open Student Information System. It's an application
 * designed to manage the core business of higher education institutions,
 * such as universities, faculties, institutes and professional schools.
 * The core business involves the administration of students, teachers,
 * courses, programs and so on.
 *
 * Copyright (C) 2015-2023 Université catholique de Louvain (http://www.uclouvain.be)
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * A copy of this license - GNU General Public License - is available
 * at the root of the source code of this program.  If not,
 * see http://www.gnu.org/licenses/.
 *
 */
import { mergeConfig } from 'vite';
import vue from '@vitejs/plugin-vue';



const config = {
  stories: [
    '../**/*.stories.@(js|jsx|ts|tsx)',
  ],
  staticDirs: [
    { from: '../assets', to: '/' },
    { from: '../../osis_document_components/static', to: '/static' },
  ],
  addons: [
    '@storybook/addon-essentials',
    '@storybook/addon-interactions',
  ],
  framework: {
    name: '@storybook/vue3-vite',
    options: {},
  },
  async viteFinal(baseConfig, { configType }) {
    // Ajouter le support des fichiers .vue
    let finalConfig = mergeConfig(baseConfig, {
      plugins: [
          vue(),
      ],
    });

    if (configType === 'PRODUCTION') {
      finalConfig = mergeConfig(finalConfig, {
        base: './',
        build: {
          rollupOptions: {
            output: {
              sanitizeFileName: (name) => {
                /** Same as original but replace '_' by '' for storybook deployment
                 * See https://github.com/rollup/rollup/blob/master/src/utils/sanitizeFileName.ts */
                const INVALID_CHAR_REGEX = /[\u0000-\u001F"#$&*+,:;<=>?[\]^`{|}\u007F]/g;
                const DRIVE_LETTER_REGEX = /^[a-z]:/i;
                const match = DRIVE_LETTER_REGEX.exec(name);
                const driveLetter = match ? match[0] : '';
                return driveLetter + name
                  .slice(driveLetter.length)
                  .replace(INVALID_CHAR_REGEX, '')
                  .replace(/_/g, ''); // enlève les underscores
              },
            },
          },
        },
      });
    }
    return finalConfig;
  },
};

export default config;
