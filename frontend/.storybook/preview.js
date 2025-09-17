/*
 *
 *   OSIS stands for Open Student Information System. It's an application
 *   designed to manage the core business of higher education institutions,
 *   such as universities, faculties, institutes and professional schools.
 *   The core business involves the administration of students, teachers,
 *   courses, programs and so on.
 *
 *   Copyright (C) 2015-2021 Université catholique de Louvain (http://www.uclouvain.be)
 *
 *   This program is free software: you can redistribute it and/or modify
 *   it under the terms of the GNU General Public License as published by
 *   the Free Software Foundation, either version 3 of the License, or
 *   (at your option) any later version.
 *
 *   This program is distributed in the hope that it will be useful,
 *   but WITHOUT ANY WARRANTY; without even the implied warranty of
 *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *   GNU General Public License for more details.
 *
 *   A copy of this license - GNU General Public License - is available
 *   at the root of the source code of this program.  If not,
 *   see http://www.gnu.org/licenses/.
 *
 */
import {i18n} from '../i18n';
import { setup } from '@storybook/vue3-vite';

setup((app) => {
  app.use(i18n);
});

export const globalTypes = {
  locale: {
    name: 'Locale',
    description: 'Langue d\'affichage',
    toolbar: {
      icon: 'globe',
      items: [
        { value: 'fr', right: '🇫🇷', title: 'Français' },
        { value: 'en', right: '🇺🇸', title: 'English' }
      ],
      showName: true,
      dynamicTitle: true
    },
  },
};

const withI18n = (story, context) => {
  const { locale } = context.globals;
  if (locale) {
    i18n.global.locale.value = locale;
  }
  return story();
};

const preview = {
    initialGlobals: {
        locale: "fr",
    },
    decorators: [withI18n],
    parameters: {
        actions: {argTypesRegex: '^on[A-Z].*'},
        controls: {
            matchers: {
                color: /(background|color)$/i,
        date: /Date$/,
      },
    },
  },
};

export default preview;