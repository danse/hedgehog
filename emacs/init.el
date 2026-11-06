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

;; Start ghci from the project root, not from live/.
(defun hedgehog-start ()
  "Start (or restart) the Tidal ghci process from the project root."
  (interactive)
  (let ((default-directory hedgehog-root))
    (tidal-start-haskell)))

(defun hedgehog--statement-start-p (line)
  "Return non-nil if LINE starts a new top-level Tidal statement."
  (and (string-match-p "\\`[^ \t\n]" line)
       (not (string-match-p "\\`[ \t]*--" line))
       (not (string-match-p "\\`[ \t]*$" line))))

(defun hedgehog--group-statements (text)
  "Split TEXT into statement groups, keeping indented continuation lines together."
  (let ((lines (split-string text "\n"))
        groups current)
    (dolist (line lines)
      (cond
       ((hedgehog--statement-start-p line)
        (when current
          (push (string-join (nreverse current) "\n") groups))
        (setq current (list line)))
       (current
        (push line current))
       ((not (string-match-p "\\`[ \t]*$" line))
        (push (list line) nil) ;; ignored; shouldn't happen
        (setq current (list line)))))
    (when current
      (push (string-join (nreverse current) "\n") groups))
    (seq-filter (lambda (s) (not (string-match-p "\\`[ \t]*\\(--.*\\)?[ \t]*\\'" s)))
                (nreverse groups))))

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

;; Keys --------------------------------------------------------------------
(defun hedgehog-tidal-keys ()
  (local-set-key (kbd "C-c C-s") #'hedgehog-start)
  (local-set-key (kbd "C-c C-c") #'tidal-run-line)
  (local-set-key (kbd "C-RET")   #'hedgehog-eval-block)
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
