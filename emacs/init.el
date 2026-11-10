;;; init.el --- Hedgehog: project-contained Tidal/Emacs setup -*- lexical-binding: t; -*-

;; Launch with:
;;   emacs --init-directory /home/marea/hub/hedgehog/emacs
;; or simply:
;;   scripts/edit.sh [file.tidal]

;;; Code:

;; Reuse the haskell-mode already installed in ~/.emacs.d/elpa.
(setq package-user-dir (expand-file-name "~/.emacs.d/elpa"))
(require 'package)
(package-initialize)

(defvar hedgehog-root
  (file-name-directory (directory-file-name user-emacs-directory))
  "Root directory of the hedgehog project.")

(add-to-list 'load-path (expand-file-name "lisp" user-emacs-directory))

;; haskell-mode 20230511 does a top-level
;;   (add-to-list 'flymake-allowed-file-name-masks ...)
;; Emacs 30 removed that variable (it was only obsolete in 29), so the
;; require aborts before tidal.el loads. This project does not use
;; flymake, so just give the symbol a value.
(unless (boundp 'flymake-allowed-file-name-masks)
  (defvar flymake-allowed-file-name-masks nil))

(require 'haskell-mode)
(require 'tidal)

;; tidal.el settings -------------------------------------------------------
(setq tidal-interpreter "ghci")
(setq tidal-interpreter-arguments nil)
(setq tidal-buffer "*tidal*")
(setq tidal-literate-p nil)
(setq tidal-boot-script-path
      (expand-file-name "boot/BootTidal.hs" hedgehog-root))

;; Start ghci from the project root, not from tracks/.
(defun hedgehog-start ()
  "Start (or restart) the Tidal ghci process from the project root."
  (interactive)
  (let ((default-directory hedgehog-root))
    (tidal-start-haskell)))

(defun hedgehog--line-indent (line)
  "Return the indentation width of LINE.
Tabs advance to the next multiple of 8 columns."
  (let ((col 0)
        (i 0)
        (len (length line))
        done)
    (while (and (< i len) (not done))
      (let ((ch (aref line i)))
        (cond
         ((eq ch ?\s) (setq col (1+ col)))
         ((eq ch ?\t) (setq col (+ col 8 (- (mod col 8)))))
         (t (setq done t))))
      (setq i (1+ i)))
    col))

(defun hedgehog--blank-line-p (line)
  "Return non-nil if LINE is empty or contains only whitespace."
  (string-match-p "\\`[ \t]*\\'" line))

(defun hedgehog--comment-line-p (line)
  "Return non-nil if LINE is a comment-only line."
  (string-match-p "\\`[ \t]*--" line))

(defun hedgehog--continuation-start-p (line)
  "Return non-nil if LINE begins with a continuation operator.
Continuation lines stay with the preceding statement even when they are
not indented, for example a leading `#' operator."
  (string-match-p
   "\\`[ \t]*\\(?:#\\|\\$\\|\\.\\||\\|,\\|[][(){}]\\|>\\|=\\|<-\\)"
   line))

(defun hedgehog--strong-statement-start-p (line)
  "Return non-nil if LINE clearly begins a new Tidal top-level action.
This splits consecutive, inconsistently indented orbit/xfade lines even
when they sit deeper than the region's base indentation."
  (string-match-p
   "\\`[ \t]*\\(?:d[0-9]+\\|xfadeIn\\|xfade\\|fadeIn\\|fadeOut\\|setbpm\\|hush\\)\\(?:[ \t]\\|\\'\\)"
   line))

(defun hedgehog--base-indent (lines)
  "Return the smallest indentation among the code lines in LINES."
  (let (base)
    (dolist (line lines)
      (unless (or (hedgehog--blank-line-p line)
                  (hedgehog--comment-line-p line))
        (let ((n (hedgehog--line-indent line)))
          (setq base (if base (min base n) n)))))
    (or base 0)))

(defun hedgehog--group-statements (text)
  "Split TEXT into top-level Tidal statement groups.
Indented lines normally continue the current statement, while lines at
the region's base indentation (or clear `dN'/`xfade... actions) begin a
new one.  Blank lines are ignored.  Comments stay with the statement
they describe."
  (let* ((lines (split-string text "\n"))
         (base (hedgehog--base-indent lines))
         (groups nil)
         (current nil)          ; reversed lines of the current group
         (pending-comments nil) ; reversed comments before the next group
         in-let)
    (dolist (line lines)
      (cond
       ((hedgehog--blank-line-p line)
        nil)
       ((hedgehog--comment-line-p line)
        ;; A comment indented inside the current statement belongs to it
        ;; (notably inside a `let' block); a comment at base level is a
        ;; header for the next statement.
        (if (and current
                 (or in-let
                     (> (hedgehog--line-indent line) base)))
            (push line current)
          (push line pending-comments)))
       ((and (not (hedgehog--continuation-start-p line))
             (or (<= (hedgehog--line-indent line) base)
                 (and (not in-let)
                      (hedgehog--strong-statement-start-p line))))
        (when current
          (push (string-join (nreverse current) "\n") groups))
        (setq current (cons line pending-comments)
              pending-comments nil
              in-let (string-match-p "\\`[ \t]*let\\(?:[ \t]\\|\\'\\)" line)))
       (current
        (push line current))
       (t
        ;; Orphan indented line: start a group with it anyway.
        (setq current (cons line pending-comments)
              pending-comments nil
              in-let (string-match-p "\\`[ \t]*let\\(?:[ \t]\\|\\'\\)" line)))))
    (when current
      (push (string-join (nreverse current) "\n") groups))
    (nreverse groups)))

(defun hedgehog-send-region (beg end)
  "Send BEG..END to Tidal, grouping multi-line statements.
Adjacent top-level statements are sent separately to avoid GHCi parse issues."
  (interactive "r")
  (when (= beg end)
    (user-error "Empty region"))
  (let* ((text (buffer-substring-no-properties beg end))
         (groups (hedgehog--group-statements text)))
    (when (null groups)
      (user-error "No statements to send"))
    (dolist (stmt groups)
      (if (string-match-p "\n" stmt)
          (progn
            (tidal-send-string ":{")
            (tidal-send-string stmt)
            (tidal-send-string ":}"))
        (tidal-send-string stmt)))))

(defun hedgehog-eval-block ()
  "Evaluate the blank-line-separated block around point."
  (interactive)
  (save-mark-and-excursion
    (mark-paragraph)
    (hedgehog-send-region (region-beginning) (region-end))
    (pulse-momentary-highlight-region (region-beginning) (region-end))))

(defun hedgehog-hush ()
  "Silence all Tidal orbits."
  (interactive)
  (tidal-hush)
  (message "hush"))

;; Tidal REPL completion ---------------------------------------------------
(defconst hedgehog-tidal-orbit-names
  (append (mapcar (lambda (n) (format "d%d" n)) (number-sequence 1 16))
          (mapcar (lambda (n) (format "d%d_" n)) (number-sequence 1 16)))
  "Orbit names defined by BootTidal.hs.")

(defun hedgehog--tidal-source-buffer-p (buffer)
  "Return non-nil if BUFFER contains Tidal source."
  (with-current-buffer buffer
    (or (derived-mode-p 'tidal-mode)
        (and buffer-file-name
             (string-match-p "\\.\\(?:l\\)?tidal\\'" buffer-file-name)))))

(defun hedgehog--tidal-buffer-words ()
  "Collect identifiers from all open Tidal source buffers."
  (let (words)
    (dolist (buffer (buffer-list))
      (when (and (buffer-live-p buffer)
                 (hedgehog--tidal-source-buffer-p buffer))
        (with-current-buffer buffer
          (save-excursion
            (goto-char (point-min))
            (while (re-search-forward "[[:alpha:]_][[:alnum:]_']*" nil t)
              ;; Keep words from commented-out code too: they are useful
              ;; when uncommenting an alternative.
              (push (match-string-no-properties 0) words))))))
    words))

(defun hedgehog--tidal-history-words ()
  "Collect words from the current comint input history."
  (let (words)
    (when (bound-and-true-p comint-input-ring)
      (dolist (entry (ring-elements comint-input-ring))
        (dolist (word (split-string entry "[^[:alnum:]_']+" t))
          (push word words))))
    words))

(defun hedgehog--tidal-completion-bounds ()
  "Return the bounds of the Tidal identifier at point, or nil.
Unlike `bounds-of-thing-at-point', this treats a trailing apostrophe
as part of the name (for example `substruct'')."
  (let ((beg (save-excursion
               (skip-chars-backward "[:alnum:]_'")
               (point)))
        (end (save-excursion
               (skip-chars-forward "[:alnum:]_'")
               (point))))
    (when (< beg end)
      (cons beg end))))

(defun hedgehog-tidal-completion-at-point ()
  "Complete Tidal identifiers from open Tidal buffers and the REPL history."
  (let ((bounds (hedgehog--tidal-completion-bounds)))
    (when bounds
      (let* ((beg (car bounds))
             (end (cdr bounds))
             (prefix (buffer-substring-no-properties beg end)))
        (when (and (> (length prefix) 0)
                   ;; Leave GHCi :commands and comint history alone.
                   (not (eq (char-before beg) ?:)))
          (let* ((candidates
                  (delete-dups
                   (append hedgehog-tidal-orbit-names
                           (hedgehog--tidal-buffer-words)
                           (hedgehog--tidal-history-words))))
                 (matches (all-completions prefix candidates)))
            (when matches
              (list beg end (sort matches #'string<)))))))))

(defun hedgehog--tidal-repl-setup ()
  "Use `completion-at-point' for Tab in the *tidal* REPL."
  (when (and (boundp 'tidal-buffer)
             (string= (buffer-name) tidal-buffer))
    (setq-local completion-at-point-functions
                '(hedgehog-tidal-completion-at-point
                  comint-completion-at-point))
    ;; `local-set-key' edits the shared `comint-mode-map', which would
    ;; change Tab in every comint buffer.  Give this buffer its own map
    ;; with the normal comint map as parent instead.
    (let ((map (make-sparse-keymap)))
      (set-keymap-parent map (current-local-map))
      (use-local-map map)
      (local-set-key (kbd "TAB") #'completion-at-point))))

(add-hook 'comint-mode-hook #'hedgehog--tidal-repl-setup)

;; Keys --------------------------------------------------------------------
(defun hedgehog-tidal-keys ()
  (local-set-key (kbd "C-c C-s") #'hedgehog-start)
  (local-set-key (kbd "C-c C-c") #'tidal-run-line)
  ;; tidal.el binds `C-<return>' to tidal-run-multiple-lines.  `C-RET' is a
  ;; different event, so bind both physical forms to the project sender.
  (local-set-key (kbd "C-<return>") #'hedgehog-eval-block)
  (local-set-key (kbd "C-RET")      #'hedgehog-eval-block)
  (local-set-key (kbd "C-c C-e") #'hedgehog-eval-block)
  (local-set-key (kbd "C-c C-r") #'hedgehog-send-region)
  (local-set-key (kbd "C-c C-h") #'hedgehog-hush)
  (local-set-key (kbd "C-c C-k") #'hedgehog-hush)
  (local-set-key (kbd "C-c C-i") #'tidal-interrupt-haskell)
  (local-set-key (kbd "C-c C-v") #'tidal-see-output)
  (local-set-key (kbd "C-c C-q") #'tidal-quit-haskell))

(add-hook 'tidal-mode-hook #'hedgehog-tidal-keys)
(add-hook 'literate-tidal-mode-hook #'hedgehog-tidal-keys)

;; Quality of life ---------------------------------------------------------
(setq inhibit-startup-screen t)
(setq ring-bell-function 'ignore)
(setq make-backup-files nil)
(setq auto-save-default nil)
(show-paren-mode 1)
(column-number-mode 1)
(scroll-bar-mode -1)

(setq custom-file (expand-file-name "custom.el" user-emacs-directory))
(when (file-exists-p custom-file)
  (load custom-file))

(provide 'init)
;;; init.el ends here
