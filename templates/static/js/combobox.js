/* ==========================================================================
   combobox.js — Selector con buscador integrado (T5.4)
   --------------------------------------------------------------------------
   Reemplaza el patrón anterior de "input de filtro por encima + <select>
   aparte", que obligaba a escribir en un campo y elegir en otro, y que además
   ocultaba las opciones con `option.style.display`, algo que ni siquiera
   funciona igual en todos los navegadores.

   Cómo se usa desde una plantilla: basta con marcar el <select> de siempre.

       <select name="id_paciente" class="form-select" data-combobox
               data-combobox-placeholder="Escriba para buscar un paciente..."
               required>

   Principios de esta implementación (no son detalles menores):

   1. **El <select> original se conserva y sigue siendo el que envía el dato.**
      Solo se oculta. El formulario manda exactamente el mismo `name` y el
      mismo `value` que antes, así que ninguna ruta del backend cambia.
   2. **El texto se pinta con `textContent`, nunca con `innerHTML`.** Los
      nombres de pacientes y medicamentos son texto libre escrito por los
      usuarios; construir HTML a mano con esos valores fue exactamente el
      XSS almacenado que hubo que cerrar en el modal de detalle. Aquí no se
      concatena HTML en ningún punto, así que el problema no puede aparecer.
   3. **`required` se traslada al input visible.** Un <select> con `display:
      none` y `required` hace que Chrome bloquee el envío con "An invalid form
      control is not focusable" — el formulario deja de funcionar y el usuario
      no ve ningún mensaje. Con el `required` en el input visible, el navegador
      muestra su aviso normal sobre el campo correcto.
   4. **Sin JavaScript el formulario sigue sirviendo**: queda el <select>
      nativo tal cual, con su `required` intacto.
   ========================================================================== */
(function () {
	'use strict';

	/* Normaliza para comparar: minúsculas y sin tildes, para que "Quiñones"
	   se encuentre escribiendo "quinones" y "Angel" encuentre "Ángel". */
	function normalizar(texto) {
		return (texto || '').toString().toLowerCase()
			.normalize('NFD').replace(/[\u0300-\u036f]/g, '');
	}

	var contador = 0;

	function crear(select) {
		if (select.dataset.comboboxListo === '1') return;
		select.dataset.comboboxListo = '1';

		contador += 1;
		var idLista = 'combobox-lista-' + contador;

		/* Una <option> vacía y `disabled` es solo el texto de ayuda
		   ("-- Seleccionar paciente --"), no una opción elegible. Una vacía
		   pero habilitada sí lo es (p. ej. "-- Sin usuario vinculado --" en
		   pacientes, donde "ninguno" es una respuesta válida). */
		var todas = Array.prototype.slice.call(select.options);
		var ayuda = null;
		var opciones = [];
		todas.forEach(function (op) {
			if (op.value === '' && op.disabled) { ayuda = op; return; }
			opciones.push({ value: op.value, label: op.textContent.trim(), option: op });
		});

		var contenedor = document.createElement('div');
		contenedor.className = 'combobox';

		var input = document.createElement('input');
		input.type = 'text';
		input.className = 'form-control combobox-input';
		input.autocomplete = 'off';
		input.setAttribute('role', 'combobox');
		input.setAttribute('aria-expanded', 'false');
		input.setAttribute('aria-autocomplete', 'list');
		input.setAttribute('aria-controls', idLista);
		input.placeholder = select.dataset.comboboxPlaceholder ||
			(ayuda ? ayuda.textContent.trim() : 'Escriba para buscar...');
		if (select.required) {
			select.required = false;   // ver principio 3 arriba
			input.required = true;
		}
		if (select.disabled) input.disabled = true;

		var caret = document.createElement('span');
		caret.className = 'combobox-caret';
		var icono = document.createElement('i');
		icono.className = 'bi bi-chevron-down';
		caret.appendChild(icono);

		var lista = document.createElement('ul');
		lista.className = 'combobox-list';
		lista.id = idLista;
		lista.setAttribute('role', 'listbox');
		lista.hidden = true;

		/* Un <li> por opción, con el texto puesto con textContent. */
		var items = opciones.map(function (op, i) {
			var li = document.createElement('li');
			li.className = 'combobox-option';
			li.id = idLista + '-op-' + i;
			li.setAttribute('role', 'option');
			li.setAttribute('aria-selected', 'false');
			li.dataset.valor = op.value;
			li.textContent = op.label;
			lista.appendChild(li);
			return li;
		});

		var vacio = document.createElement('li');
		vacio.className = 'combobox-empty';
		vacio.textContent = 'Sin resultados';
		vacio.hidden = true;
		lista.appendChild(vacio);

		select.parentNode.insertBefore(contenedor, select);
		contenedor.appendChild(input);
		contenedor.appendChild(caret);
		contenedor.appendChild(lista);
		contenedor.appendChild(select);
		select.classList.add('combobox-native');
		select.setAttribute('tabindex', '-1');
		select.setAttribute('aria-hidden', 'true');
		select.removeAttribute('size');   // los `size="4"` ya no aplican

		var visibles = items.slice();
		var activo = -1;

		/* Última selección válida. Se guarda aparte del <select> porque
		   mientras el usuario escribe se vacía el <select> (un texto a
		   medias no es una selección), y sin esta memoria un Escape o un
		   clic fuera dejarían el campo vacío en vez de devolverlo a lo que
		   ya estaba elegido. */
		var seleccion = { value: '', label: '' };

		function etiquetaDe(valor) {
			var elegida = opciones.filter(function (op) { return op.value === valor; })[0];
			/* Si el <select> venía sin selección real (solo el texto de
			   ayuda), no hay etiqueta que mostrar. */
			if (!elegida) return '';
			if (elegida.value === '' && select.selectedIndex < 0) return '';
			return elegida.label;
		}

		function restaurarSeleccion() {
			select.value = seleccion.value;
			input.value = seleccion.label;
		}

		function marcarActivo(indice) {
			items.forEach(function (li) { li.classList.remove('is-active'); });
			activo = indice;
			if (indice >= 0 && visibles[indice]) {
				var li = visibles[indice];
				li.classList.add('is-active');
				input.setAttribute('aria-activedescendant', li.id);
				/* Mantiene visible la opción activa al navegar con el teclado. */
				var arriba = li.offsetTop;
				var abajo = arriba + li.offsetHeight;
				if (arriba < lista.scrollTop) lista.scrollTop = arriba;
				else if (abajo > lista.scrollTop + lista.clientHeight) lista.scrollTop = abajo - lista.clientHeight;
			} else {
				input.removeAttribute('aria-activedescendant');
			}
		}

		function filtrar(texto) {
			var buscado = normalizar(texto);
			visibles = [];
			items.forEach(function (li, i) {
				var coincide = !buscado || normalizar(opciones[i].label).indexOf(buscado) !== -1;
				li.hidden = !coincide;
				if (coincide) visibles.push(li);
			});
			vacio.hidden = visibles.length > 0;
			marcarActivo(visibles.length ? 0 : -1);
		}

		function abrir(mostrarTodo) {
			if (select.disabled) return;
			filtrar(mostrarTodo ? '' : input.value);
			lista.hidden = false;
			input.setAttribute('aria-expanded', 'true');
			/* Si ya había algo elegido, se resalta en vez de la primera. */
			var indiceElegido = -1;
			visibles.forEach(function (li, i) {
				if (li.dataset.valor === select.value && select.value !== '') indiceElegido = i;
			});
			if (indiceElegido >= 0) marcarActivo(indiceElegido);
		}

		function cerrar() {
			lista.hidden = true;
			input.setAttribute('aria-expanded', 'false');
			input.removeAttribute('aria-activedescendant');
			items.forEach(function (li) { li.classList.remove('is-active'); });
			activo = -1;
		}

		function elegir(li) {
			select.value = li.dataset.valor;
			input.value = li.textContent;
			seleccion = { value: li.dataset.valor, label: li.textContent };
			items.forEach(function (otro) {
				otro.setAttribute('aria-selected', otro === li ? 'true' : 'false');
			});
			/* Se dispara `change` por si algo más de la página escucha el
			   <select> (la pantalla de disponibilidad lo lee, por ejemplo). */
			select.dispatchEvent(new Event('change', { bubbles: true }));
			cerrar();
		}

		/* Estado inicial: refleja lo que el <select> ya traía seleccionado
		   (una edición precargada, o el valor que el usuario había enviado
		   antes de un error de validación). */
		seleccion = { value: select.value, label: etiquetaDe(select.value) };
		if (seleccion.label === '') seleccion.value = '';
		input.value = seleccion.label;
		items.forEach(function (li) {
			if (li.dataset.valor === select.value && input.value !== '') li.setAttribute('aria-selected', 'true');
		});

		input.addEventListener('focus', function () { abrir(true); input.select(); });
		input.addEventListener('mousedown', function () {
			if (lista.hidden && document.activeElement === input) abrir(true);
		});

		input.addEventListener('input', function () {
			/* Mientras se escribe no hay una opción elegida: si el usuario
			   deja el texto a medias, no debe quedar seleccionado el valor
			   anterior sin que se note. */
			select.value = '';
			abrir(false);
		});

		input.addEventListener('keydown', function (e) {
			if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
				e.preventDefault();
				if (lista.hidden) { abrir(true); return; }
				if (!visibles.length) return;
				var siguiente = e.key === 'ArrowDown' ? activo + 1 : activo - 1;
				if (siguiente < 0) siguiente = visibles.length - 1;
				if (siguiente >= visibles.length) siguiente = 0;
				marcarActivo(siguiente);
			} else if (e.key === 'Enter') {
				if (!lista.hidden && activo >= 0 && visibles[activo]) {
					/* Sin esto, Enter enviaría el formulario en vez de
					   elegir la opción resaltada. */
					e.preventDefault();
					elegir(visibles[activo]);
				}
			} else if (e.key === 'Escape') {
				if (!lista.hidden) {
					e.preventDefault();
					restaurarSeleccion();
					cerrar();
				}
			} else if (e.key === 'Tab') {
				cerrar();
			}
		});

		/* `mousedown` en vez de `click`: el clic en la lista provocaría
		   primero el blur del input, que cierra la lista, y el clic se
		   perdería. Con preventDefault el input no pierde el foco. */
		lista.addEventListener('mousedown', function (e) {
			var li = e.target.closest('.combobox-option');
			if (!li) return;
			e.preventDefault();
			elegir(li);
		});

		input.addEventListener('blur', function () {
			cerrar();
			/* Si quedó texto escrito que no corresponde a ninguna opción,
			   se vuelve a la última selección válida (o a vacío si nunca
			   hubo una, y entonces `required` hace su trabajo). El campo
			   nunca queda mostrando un texto que no es una selección real. */
			restaurarSeleccion();
		});
	}

	function iniciar() {
		document.querySelectorAll('select[data-combobox]').forEach(crear);
	}

	if (document.readyState === 'loading') {
		document.addEventListener('DOMContentLoaded', iniciar);
	} else {
		iniciar();
	}
})();
