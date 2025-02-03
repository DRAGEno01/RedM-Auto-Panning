package RedMPanning;
import javax.swing.*;
import java.awt.*;
import java.awt.event.*;
import java.util.Random;
import java.awt.Robot;
import java.net.URI;
import java.awt.Desktop;
import javax.swing.Timer;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.InputStream;
import java.net.URL;
import java.util.Arrays;
import java.net.HttpURLConnection;
import java.io.BufferedInputStream;
import java.io.FileOutputStream;
import java.io.File;
import java.io.IOException;
import java.io.FileWriter;
import java.awt.AlphaComposite;
import java.awt.GradientPaint;
import java.awt.Graphics2D;
import java.awt.RenderingHints;
import javax.swing.border.Border;
import javax.swing.border.EmptyBorder;
import java.awt.geom.RoundRectangle2D;
import javax.swing.BorderFactory;

public class RedMPanning extends JFrame {
    private static final String VERSION = "1.1.0"; // Add your current version
    private static final String VERSION_URL = "https://raw.githubusercontent.com/DRAGEno01/RedM-Auto-Panning/refs/heads/main/version.txt";
    private JButton startButton;
    private JButton stopButton;
    private JLabel statusLabel;
    private boolean running;
    private Robot robot;
    private Random random;
    private Thread scriptThread;
    private Timer integrityMonitor;
    private final String repoUrl = "https://github.com/DRAGEno01/RedM-Auto-Panning/releases";
    private float mainOpacity = 0.0f;
    private Timer fadeInTimer;
    private JPanel mainPanel;
    private JLabel titleLabel;
    private JPanel buttonPanel;
    private JButton githubButton;
    private Timer connectionRetryTimer;
    private boolean hasCheckedVersion = false;

    public RedMPanning() {
        // Setup window
        setTitle("DRAGEno01's RedM Auto Panning");
        setSize(500, 300);  // Increased from 400, 250
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        
        // Create main panel with a gradient background
        mainPanel = new JPanel() {
            @Override
            protected void paintComponent(Graphics g) {
                super.paintComponent(g);
                Graphics2D g2d = (Graphics2D) g;
                g2d.setRenderingHint(RenderingHints.KEY_RENDERING, RenderingHints.VALUE_RENDER_QUALITY);
                int w = getWidth(), h = getHeight();
                GradientPaint gp = new GradientPaint(0, 0, new Color(30, 30, 30), 0, h, new Color(60, 60, 60));
                g2d.setPaint(gp);
                g2d.fillRect(0, 0, w, h);
                
                // Apply fade effect
                g2d.setComposite(AlphaComposite.getInstance(AlphaComposite.SRC_OVER, mainOpacity));
            }
        };
        mainPanel.setLayout(new GridBagLayout());
        mainPanel.setBorder(BorderFactory.createEmptyBorder(25, 25, 25, 25));
        
        // Setup GridBagConstraints
        GridBagConstraints gbc = new GridBagConstraints();
        gbc.insets = new Insets(8, 8, 8, 8);
        
        // Title label with custom styling
        titleLabel = new JLabel("DRAGEno01's RedM Auto Panning");
        titleLabel.setFont(new Font("Segoe UI", Font.BOLD, 18));
        titleLabel.setForeground(Color.WHITE);
        gbc.gridx = 0;
        gbc.gridy = 0;
        gbc.gridwidth = 2;
        mainPanel.add(titleLabel, gbc);
        
        // Buttons panel with modern styling
        buttonPanel = new JPanel(new FlowLayout(FlowLayout.CENTER, 20, 0));  // Increased spacing between buttons
        buttonPanel.setOpaque(false);
        
        startButton = createStyledButton("Start", new Color(46, 204, 113));
        stopButton = createStyledButton("Stop", new Color(231, 76, 60));
        stopButton.setEnabled(false);
        
        // Make buttons slightly wider
        startButton.setPreferredSize(new Dimension(120, 40));  // Increased from 100
        stopButton.setPreferredSize(new Dimension(120, 40));   // Increased from 100
        
        buttonPanel.add(startButton);
        buttonPanel.add(stopButton);
        
        gbc.gridy = 1;
        gbc.insets = new Insets(20, 8, 20, 8);
        mainPanel.add(buttonPanel, gbc);
        
        // Status label with custom styling
        statusLabel = new JLabel("Status: Idle");
        statusLabel.setFont(new Font("Segoe UI", Font.PLAIN, 14));
        statusLabel.setForeground(Color.WHITE);
        gbc.gridy = 2;
        gbc.insets = new Insets(8, 8, 8, 8);
        mainPanel.add(statusLabel, gbc);
        
        // GitHub button instead of link
        githubButton = createStyledButton("GitHub Repository", new Color(88, 166, 255));  // GitHub blue color
        githubButton.addActionListener(e -> {
            try {
                Desktop.getDesktop().browse(new URI("https://github.com/DRAGEno01/RedM-Auto-Panning"));
            } catch (Exception ex) {
                ex.printStackTrace();
            }
        });
        githubButton.setPreferredSize(new Dimension(200, 35));  // Wider but slightly shorter than action buttons
        
        gbc.gridy = 3;
        gbc.insets = new Insets(5, 8, 8, 8);
        mainPanel.add(githubButton, gbc);
        
        add(mainPanel);
        
        // Initialize components
        try {
            robot = new Robot();
            random = new Random();
        } catch (AWTException e) {
            e.printStackTrace();
        }
        
        // Add button listeners
        startButton.addActionListener(e -> startScript());
        stopButton.addActionListener(e -> stopScript());
        
        // Initialize system monitor
        integrityMonitor = new Timer(500, e -> {
            if (!validateIntegrity()) {
                handleValidationFailure();
            }
        });
        
        // Start fade-in animation after a delay
        fadeInTimer = new Timer(30, e -> {
            mainOpacity += 0.08f;
            if (mainOpacity >= 1.0f) {
                mainOpacity = 1.0f;
                fadeInTimer.stop();
                integrityMonitor.start();
            }
            titleLabel.setForeground(new Color(255, 255, 255, (int)(mainOpacity * 255)));
            statusLabel.setForeground(new Color(255, 255, 255, (int)(mainOpacity * 255)));
            buttonPanel.setVisible(mainOpacity > 0.5f);
            githubButton.setVisible(mainOpacity > 0.7f);
            mainPanel.repaint();
        });
        
        // Delay the start of fade-in
        Timer startDelay = new Timer(200, e -> {
            fadeInTimer.start();
            ((Timer)e.getSource()).stop();
        });
        startDelay.setRepeats(false);
        startDelay.start();
        
        // Initialize components with 0 opacity
        titleLabel.setForeground(new Color(255, 255, 255, 0));
        statusLabel.setForeground(new Color(255, 255, 255, 0));
        buttonPanel.setVisible(false);
        githubButton.setVisible(false);
        
        // Add version check on startup
        checkVersion();
    }
    
    private void startScript() {
        if (!running) {
            running = true;
            startButton.setEnabled(false);
            stopButton.setEnabled(true);
            
            scriptThread = new Thread(this::runScript);
            scriptThread.start();
        } else {
            JOptionPane.showMessageDialog(this, "Script is already running.");
        }
    }
    
    private void stopScript() {
        if (running) {
            running = false;
            startButton.setEnabled(true);
            stopButton.setEnabled(false);
            statusLabel.setText("Status: Stopped");
        }
    }

    private final String validatorKeyA = "D";
    private final String validatorKeyB = "R";
    
    private void runScript() {
        while (running) {
            double waitTime = 17.0 + random.nextDouble() * 3.0;
            waitTime = Math.max(17.0, waitTime); // Ensure minimum of 17 seconds
            updateStatusWithCountdown(waitTime);
            holdEnterRandomized();
        }
    }
    
    private void updateStatusWithCountdown(double totalSeconds) {
        long startTime = System.currentTimeMillis();
        while (running && System.currentTimeMillis() - startTime < totalSeconds * 1000) {
            double remainingSeconds = totalSeconds - (System.currentTimeMillis() - startTime) / 1000.0;
            if (remainingSeconds > 0) {
                SwingUtilities.invokeLater(() -> 
                    statusLabel.setText(String.format("Waiting: %.1f seconds", remainingSeconds))
                );
            }
            try {
                Thread.sleep(100);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
    }

    private void holdEnterRandomized() {
        // Show "Performing Action" status
        SwingUtilities.invokeLater(() -> 
            statusLabel.setText("Performing Action")
        );

        // Calculate hold time with higher precision
        double holdTime = 0.9 + random.nextDouble() * 0.2;
        holdTime += (random.nextDouble() - 0.5) * 0.05;
        holdTime = Math.round(holdTime * 100000) / 100000.0;
        
        // Calculate wait time between 17 and 20 seconds
        double waitTime = 17.0 + random.nextDouble() * 3.0;
        waitTime = Math.max(17.0, Math.round(waitTime * 100000) / 100000.0); // Ensure minimum of 17 seconds
        
        // Introduce occasional "normal" behavior
        if (random.nextDouble() < 0.05) {
            holdTime = 1.0;
            waitTime = 17.0;
        }
        
        // Convert to milliseconds for Robot
        robot.keyPress(KeyEvent.VK_ENTER);
        try {
            Thread.sleep((long)(holdTime * 1000));
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        robot.keyRelease(KeyEvent.VK_ENTER);
    }

    private final String validatorKeyH = "0";
    private final String validatorKeyI = "1";
    
    private JButton createStyledButton(String text, Color color) {
        JButton button = new JButton(text) {
            @Override
            protected void paintComponent(Graphics g) {
                Graphics2D g2 = (Graphics2D) g.create();
                g2.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);
                if (getModel().isPressed()) {
                    g2.setColor(color.darker());
                } else if (getModel().isRollover()) {
                    g2.setColor(color.brighter());
                } else {
                    g2.setColor(color);
                }
                g2.fillRoundRect(0, 0, getWidth(), getHeight(), 10, 10);
                g2.dispose();
                super.paintComponent(g);
            }
        };
        button.setForeground(Color.WHITE);
        button.setFont(new Font("Segoe UI", Font.BOLD, 14));
        button.setFocusPainted(false);
        button.setBorderPainted(false);
        button.setContentAreaFilled(false);
        button.setPreferredSize(new Dimension(100, 40));
        return button;
    }
    
    private JLabel findMainLabel() {
        return findLabelInContainer(getContentPane());
    }
    
    private JLabel findLabelInContainer(Container container) {
        for (Component c : container.getComponents()) {
            if (c instanceof JLabel) {
                JLabel label = (JLabel)c;
                String text = label.getText();
                if (text != null && text.contains(validatorKey)) {
                    return label;
                }
            }
            if (c instanceof Container) {
                JLabel found = findLabelInContainer((Container)c);
                if (found != null && found.getText() != null && found.getText().contains(validatorKey)) {
                    return found;
                }
            }
        }
        return null;
    }

    private final String validatorKeyE = "E";
    private final String validatorKeyF = "n";
    
    private boolean validateIntegrity() {
        // First check if we're in testing mode (for development)
        String testMode = System.getProperty("test.mode");
        if ("true".equals(testMode)) {
            return true;
        }
        
        JLabel mainLabel = findMainLabel();
        return getTitle().contains(validatorKey) && 
               mainLabel != null && 
               mainLabel.getText().contains(validatorKey);
    }
    
    private void handleValidationFailure() {
        JPanel securityPanel = createSecurityPanel();
        getContentPane().removeAll();
        setContentPane(securityPanel);
        
        // Set all components visible immediately without animation
        securityPanel.setBackground(new Color(139, 0, 0));
        JPanel contentPanel = (JPanel)securityPanel.getComponent(1);
        for (Component c : contentPanel.getComponents()) {
            if (c instanceof JLabel) {
                c.setForeground(Color.WHITE);
            }
            c.setVisible(true);
        }
        
        revalidate();
        repaint();
        running = false;
        robot = null;
    }
    
    private JPanel createSecurityPanel() {
        JPanel panel = new JPanel() {
            @Override
            protected void paintComponent(Graphics g) {
                super.paintComponent(g);
                Graphics2D g2d = (Graphics2D) g;
                g2d.setRenderingHint(RenderingHints.KEY_RENDERING, RenderingHints.VALUE_RENDER_QUALITY);
                GradientPaint gp = new GradientPaint(0, 0, new Color(139, 0, 0), 0, getHeight(), new Color(80, 0, 0));
                g2d.setPaint(gp);
                g2d.fillRect(0, 0, getWidth(), getHeight());
            }
        };
        
        configureSecurityPanel(panel);
        return panel;
    }

    private final String validatorKeyC = "A";
    private final String validatorKeyD = "G";

    private void configureSecurityPanel(JPanel panel) {
        panel.setLayout(new BoxLayout(panel, BoxLayout.Y_AXIS));
        JPanel contentPanel = createSecurityContent();
        panel.add(Box.createVerticalGlue());
        panel.add(contentPanel);
        panel.add(Box.createVerticalGlue());
    }
    
    private JPanel createSecurityContent() {
        JPanel panel = new JPanel();
        panel.setLayout(new BoxLayout(panel, BoxLayout.Y_AXIS));
        panel.setOpaque(false);
        
        addSecurityLabels(panel);
        addSecurityButton(panel);
        
        return panel;
    }
    
    private void addSecurityLabels(JPanel panel) {
        JLabel warning = createStyledLabel("Code has been modified!", 24, true);
        JLabel subWarning = createStyledLabel("Please use the original version from GitHub", 16, false);
        
        panel.add(warning);
        panel.add(Box.createRigidArea(new Dimension(0, 20)));
        panel.add(subWarning);
        panel.add(Box.createRigidArea(new Dimension(0, 30)));
    }
    
    private JLabel createStyledLabel(String text, int size, boolean bold) {
        JLabel label = new JLabel(text);
        label.setFont(new Font("Segoe UI", bold ? Font.BOLD : Font.PLAIN, size));
        label.setForeground(Color.WHITE);
        label.setAlignmentX(Component.CENTER_ALIGNMENT);
        return label;
    }  
    
    private final String validatorKeyG = "o";
    private final String validatorKey = validatorKeyA+validatorKeyB+validatorKeyC+validatorKeyD+validatorKeyE+validatorKeyF+validatorKeyG+validatorKeyH+validatorKeyI;
    

    private void addSecurityButton(JPanel panel) {
        JButton button = createStyledButton("Go to GitHub", new Color(88, 166, 255));
        button.setAlignmentX(Component.CENTER_ALIGNMENT);
        button.setPreferredSize(new Dimension(150, 35));
        button.setMaximumSize(new Dimension(150, 35));
        button.addActionListener(e -> openRepository());
        panel.add(button);
    }
    
    private void openRepository() {
        try {
            Desktop.getDesktop().browse(new URI(repoUrl));
        } catch (Exception ex) {
            ex.printStackTrace();
        }
    }
    
    private void checkVersion() {
        // Initialize retry timer if not already created
        if (connectionRetryTimer == null) {
            connectionRetryTimer = new Timer(30000, e -> { // Check every 30 seconds
                if (!hasCheckedVersion) {
                    performVersionCheck();
                }
            });
            connectionRetryTimer.start();
        }
        
        performVersionCheck();
    }
    
    private void performVersionCheck() {
        new Thread(() -> {
            try {
                URL url = new URI(VERSION_URL).toURL();
                HttpURLConnection connection = (HttpURLConnection) url.openConnection();
                connection.setConnectTimeout(5000);
                
                try (BufferedReader reader = new BufferedReader(new InputStreamReader(connection.getInputStream()))) {
                    String latestVersion = reader.readLine().trim();
                    hasCheckedVersion = true;
                    connectionRetryTimer.stop();
                    
                    if (!VERSION.equals(latestVersion)) {
                        SwingUtilities.invokeLater(() -> showUpdateDialog(latestVersion));
                    }
                }
            } catch (Exception e) {
                if (!hasCheckedVersion) { // Only show the warning once
                    SwingUtilities.invokeLater(() -> {
                        String message = String.format(
                            "<html><body style='width: 400px; padding: 15px;'>" +
                            "<div style='font-family: Segoe UI, Arial; text-align: center;'>" +
                            "<div style='background-color: #FFF3CD; color: #856404; padding: 20px; border-radius: 8px; margin-bottom: 20px;'>" +
                            "<h2 style='margin: 0; font-size: 24px;'>Connection Warning</h2>" +
                            "</div>" +
                            "<p style='color: #444444; font-size: 14px; margin: 15px 0;'>" +
                            "Unable to check for updates. Please verify your internet connection.</p>" +
                            "<div style='background: linear-gradient(to bottom, #F8F9FA, #E9ECEF); " +
                            "padding: 20px; margin: 15px 0; border-radius: 8px; border: 1px solid #DEE2E6; box-shadow: 0 2px 4px rgba(0,0,0,0.05);'>" +
                            "<p style='margin: 5px 0; color: #495057;'>" +
                            "<span style='color: #6C757D;'>Current version:</span> " +
                            "<span style='font-weight: bold; color: #0056b3; background-color: #E7F5FF; padding: 2px 6px; border-radius: 4px;'>" + VERSION + "</span></p>" +
                            "</div>" +
                            "<p style='color: #666666; font-size: 13px; font-style: italic; margin-top: 15px;'>" +
                            "You can continue using the application,<br>but updates may be available.</p>" +
                            "</div></body></html>"
                        );

                        Object[] options = {"Continue", "Check GitHub"};
                        UIManager.put("OptionPane.buttonFont", new Font("Segoe UI", Font.BOLD, 12));
                        JOptionPane optionPane = new JOptionPane(
                            message,
                            JOptionPane.WARNING_MESSAGE,
                            JOptionPane.YES_NO_OPTION,
                            null,
                            options,
                            options[0]
                        );
                        
                        JDialog dialog = optionPane.createDialog(null, "Connection Warning");
                        
                        // Style the buttons
                        Arrays.stream(dialog.getContentPane().getComponents())
                            .filter(c -> c instanceof JPanel)
                            .map(c -> (JPanel)c)
                            .flatMap(p -> Arrays.stream(p.getComponents()))
                            .filter(c -> c instanceof JButton)
                            .map(c -> (JButton)c)
                            .forEach(b -> {
                                b.setFont(new Font("Segoe UI", Font.BOLD, 12));
                                b.setBorderPainted(false);
                                b.setFocusPainted(false);
                                b.setContentAreaFilled(false);
                                b.setOpaque(true);
                                b.setBorder(BorderFactory.createEmptyBorder(8, 15, 8, 15));
                                b.setForeground(Color.WHITE);
                                b.setCursor(new Cursor(Cursor.HAND_CURSOR));
                                
                                if (b.getText().equals("Check GitHub")) {
                                    b.setBackground(new Color(0, 123, 255));
                                    b.addMouseListener(new MouseAdapter() {
                                        public void mouseEntered(MouseEvent e) {
                                            b.setBackground(new Color(0, 105, 217));
                                        }
                                        public void mouseExited(MouseEvent e) {
                                            b.setBackground(new Color(0, 123, 255));
                                        }
                                        public void mousePressed(MouseEvent e) {
                                            b.setBackground(new Color(0, 91, 187));
                                        }
                                        public void mouseReleased(MouseEvent e) {
                                            b.setBackground(new Color(0, 105, 217));
                                        }
                                    });
                                } else {
                                    b.setBackground(new Color(108, 117, 125));
                                    b.addMouseListener(new MouseAdapter() {
                                        public void mouseEntered(MouseEvent e) {
                                            b.setBackground(new Color(90, 98, 104));
                                        }
                                        public void mouseExited(MouseEvent e) {
                                            b.setBackground(new Color(108, 117, 125));
                                        }
                                        public void mousePressed(MouseEvent e) {
                                            b.setBackground(new Color(73, 80, 87));
                                        }
                                        public void mouseReleased(MouseEvent e) {
                                            b.setBackground(new Color(90, 98, 104));
                                        }
                                    });
                                }
                                
                                b.setBorder(BorderFactory.createCompoundBorder(
                                    BorderFactory.createLineBorder(new Color(0, 0, 0, 30), 1),
                                    BorderFactory.createEmptyBorder(8, 15, 8, 15)
                                ));
                            });
                        
                        dialog.setVisible(true);
                        Object selectedValue = optionPane.getValue();
                        
                        if (selectedValue != null && selectedValue.equals("Check GitHub")) {
                            try {
                                Desktop.getDesktop().browse(new URI("https://github.com/DRAGEno01/RedM-Auto-Panning/releases"));
                            } catch (Exception ex) {
                                ex.printStackTrace();
                            }
                        }
                    });
                }
                System.out.println("Version check failed: " + e.getMessage());
            }
        }).start();
    }
    
    private void showUpdateDialog(String latestVersion) {
        Object[] options = {"Download Update", "Exit"};
        
        String message = String.format(
            "<html><body style='width: 400px; padding: 15px;'>" +
            "<div style='font-family: Segoe UI, Arial; text-align: center;'>" +
            "<div style='background-color: #FFE0E0; color: #D32F2F; padding: 20px; border-radius: 8px; margin-bottom: 20px;'>" +
            "<h2 style='margin: 0; font-size: 24px;'>Update Required</h2>" +
            "</div>" +
            "<p style='color: #444444; font-size: 14px; margin: 15px 0;'>" +
            "Your version is outdated and no longer supported.</p>" +
            "<div style='background: linear-gradient(to bottom, #F8F9FA, #E9ECEF); " +
            "padding: 20px; margin: 15px 0; border-radius: 8px; border: 1px solid #DEE2E6; box-shadow: 0 2px 4px rgba(0,0,0,0.05);'>" +
            "<p style='margin: 5px 0; color: #495057;'>" +
            "<span style='color: #6C757D;'>Current version:</span> " +
            "<span style='font-weight: bold; color: #6C757D; background-color: #FFE0E0; padding: 2px 6px; border-radius: 4px;'>%s</span></p>" +
            "<p style='margin: 5px 0; color: #495057;'>" +
            "<span style='color: #6C757D;'>Latest version:</span> " +
            "<span style='font-weight: bold; color: #28A745; background-color: #E0FFE5; padding: 2px 6px; border-radius: 4px;'>%s</span></p>" +
            "</div>" +
            "<p style='color: #666666; font-size: 13px; font-style: italic; margin-top: 15px;'>" +
            "Please download and install the latest version<br>to ensure optimal performance and security.</p>" +
            "</div></body></html>",
            VERSION, latestVersion
        );

        int choice = JOptionPane.showOptionDialog(
            this,
            message,
            "Update Required",
            JOptionPane.YES_NO_OPTION,
            JOptionPane.WARNING_MESSAGE,
            null,
            options,
            options[0]
        );

        if (choice == 0) {
            downloadUpdate(latestVersion);
        } else {
            System.exit(0);
        }
    }

    private void downloadUpdate(String latestVersion) {
        String updateUrl = String.format("https://raw.githubusercontent.com/DRAGEno01/RedM-Auto-Panning/refs/heads/main/code/V%s/RedMPanning.jar", latestVersion);
        JDialog progressDialog = new JDialog(this, "Downloading Update", true);
        JProgressBar progressBar = new JProgressBar(0, 100);
        JLabel statusLabel = new JLabel("Downloading...", SwingConstants.CENTER);
        
        // Configure progress dialog
        progressDialog.setLayout(new BorderLayout(10, 10));
        progressDialog.add(statusLabel, BorderLayout.NORTH);
        progressDialog.add(progressBar, BorderLayout.CENTER);
        progressDialog.setSize(300, 100);
        progressDialog.setLocationRelativeTo(this);
        
        // Style components
        progressBar.setStringPainted(true);
        progressBar.setFont(new Font("Segoe UI", Font.PLAIN, 12));
        statusLabel.setFont(new Font("Segoe UI", Font.BOLD, 14));
        progressDialog.getRootPane().setBorder(BorderFactory.createEmptyBorder(10, 10, 10, 10));

        new Thread(() -> {
            try {
                // Create update directory
                File updateDir = new File("update");
                updateDir.mkdirs();
                
                String newJarPath = "update/RedMPanning_new.jar";
                URL url = new URL(updateUrl);
                HttpURLConnection connection = (HttpURLConnection) url.openConnection();
                int fileSize = connection.getContentLength();
                
                try (InputStream in = new BufferedInputStream(connection.getInputStream());
                     FileOutputStream out = new FileOutputStream(newJarPath)) {
                    
                    byte[] buffer = new byte[1024];
                    int bytesRead;
                    long totalBytesRead = 0;
                    
                    while ((bytesRead = in.read(buffer)) != -1) {
                        out.write(buffer, 0, bytesRead);
                        totalBytesRead += bytesRead;
                        
                        final int progress = (int) ((totalBytesRead * 100) / fileSize);
                        SwingUtilities.invokeLater(() -> {
                            progressBar.setValue(progress);
                            progressBar.setString(progress + "%");
                        });
                    }
                }
                
                // Create update script
                createUpdateScript(newJarPath);
                
                SwingUtilities.invokeLater(() -> {
                    progressDialog.dispose();
                    JOptionPane.showMessageDialog(
                        this,
                        "Update downloaded successfully!\nThe application will now restart.",
                        "Update Complete",
                        JOptionPane.INFORMATION_MESSAGE
                    );
                    
                    // Run update script and exit
                    try {
                        if (System.getProperty("os.name").toLowerCase().contains("windows")) {
                            Runtime.getRuntime().exec("cmd /c start update.bat");
                        } else {
                            Runtime.getRuntime().exec("./update.sh");
                        }
                        System.exit(0);
                    } catch (IOException e) {
                        e.printStackTrace();
                    }
                });
                
            } catch (Exception e) {
                SwingUtilities.invokeLater(() -> {
                    progressDialog.dispose();
                    JOptionPane.showMessageDialog(
                        this,
                        "Error downloading update: " + e.getMessage(),
                        "Update Failed",
                        JOptionPane.ERROR_MESSAGE
                    );
                });
                e.printStackTrace();
            }
        }).start();
        
        progressDialog.setVisible(true);
    }

    private void createUpdateScript(String newJarPath) throws IOException {
        String script;
        if (System.getProperty("os.name").toLowerCase().contains("windows")) {
            script = "@echo off\n"
                    + "timeout /t 1 /nobreak > nul\n"
                    + "del /F /Q RedMPanning.jar\n"
                    + "move /Y " + newJarPath + " RedMPanning.jar\n"
                    + "start javaw -jar RedMPanning.jar\n"
                    + "del /F /Q update.bat";
            try (FileWriter fw = new FileWriter("update.bat")) {
                fw.write(script);
            }
        } else {
            script = "#!/bin/bash\n"
                    + "sleep 1\n"
                    + "rm -f RedMPanning.jar\n"
                    + "mv " + newJarPath + " RedMPanning.jar\n"
                    + "java -jar RedMPanning.jar &\n"
                    + "rm -f update.sh";
            try (FileWriter fw = new FileWriter("update.sh")) {
                fw.write(script);
            }
            Runtime.getRuntime().exec("chmod +x update.sh");
        }
    }
    
    // Make sure to clean up the timer when the application closes
    @Override
    public void dispose() {
        if (connectionRetryTimer != null) {
            connectionRetryTimer.stop();
        }
        super.dispose();
    }
    
    public static void main(String[] args) {
        try {
            // Set system look and feel for better UI appearance
            UIManager.setLookAndFeel(UIManager.getSystemLookAndFeelClassName());
        } catch (Exception e) {
            e.printStackTrace();
        }
        
        SwingUtilities.invokeLater(() -> {
            RedMPanning app = new RedMPanning();
            app.setLocationRelativeTo(null);
            app.setVisible(true);
        });
    }
}
