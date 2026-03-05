#!/usr/bin/env python3
"""
test_ocr_debug.py — Minimal DeepSeek-OCR-2 generation diagnostic.

Tests model generation step by step to identify where 0-token generation happens.
Run with: python scripts/test_ocr_debug.py --image <path_to_image>
         python scripts/test_ocr_debug.py --text-only  (LM only, no image)
"""
import argparse
import sys
import torch

def test_lm_only(model, tokenizer, device="cuda"):
    """Test pure LM generation without image processing.
    Uses a zero/black image to avoid None-images crash in model.forward().
    """
    print("\n" + "="*50)
    print("TEST: Pure LM generation (minimal dummy image)")
    print("="*50)

    # The model requires images in forward(). Pass a tiny black image.
    # images_seq_mask all zeros → no image tokens will be embedded
    import torch
    dummy_img = torch.zeros(1, 3, 1024, 1024, device=device, dtype=torch.bfloat16)  # black patch
    dummy_ori = torch.zeros(1, 3, 640, 640, device=device, dtype=torch.bfloat16)
    images_list = [(dummy_img, dummy_ori)]

    prompt = "Hello, this is a test. The answer is:"
    inputs = tokenizer(prompt, return_tensors="pt").to(device)
    input_ids = inputs["input_ids"]
    seq_len = input_ids.shape[1]
    images_seq_mask = torch.zeros(1, seq_len, dtype=torch.bool, device=device)

    print(f"Input: '{prompt}'")
    print(f"Input shape: {input_ids.shape}")
    print(f"EOS token id: {tokenizer.eos_token_id}")
    print(f"Input token ids: {input_ids[0].tolist()}")

    with torch.no_grad():
        with torch.autocast("cuda", dtype=torch.bfloat16):
            # Single forward pass to check logits
            outputs = model(
                input_ids,
                images=images_list,
                images_seq_mask=images_seq_mask,
                images_spatial_crop=None,
                use_cache=False,
                return_dict=True,
            )
            logits = outputs.logits
            print(f"\nForward pass OK. Logits shape: {logits.shape}")

            # Check top tokens
            last_token_logits = logits[0, -1, :]
            top_tokens = torch.topk(last_token_logits, 5)
            print("Top 5 next tokens:")
            for tid, score in zip(top_tokens.indices.tolist(), top_tokens.values.tolist()):
                tok = tokenizer.decode([tid])
                print(f"  id={tid} score={score:.2f} text='{tok}'")

            # Try generation (max 10 tokens)
            # Must pass images to generate() so prepare_inputs_for_generation propagates them
            out = model.generate(
                input_ids,
                images=images_list,
                images_seq_mask=images_seq_mask,
                images_spatial_crop=None,
                max_new_tokens=10,
                do_sample=False,
                use_cache=True,
                eos_token_id=tokenizer.eos_token_id,
            )
            print(f"\nGenerated output shape: {out.shape}")
            new_tokens = out[0, input_ids.shape[1]:]
            print(f"New tokens count: {len(new_tokens)}")
            print(f"New tokens: {new_tokens.tolist()}")
            print(f"Generated text: '{tokenizer.decode(new_tokens, skip_special_tokens=False)}'")


def test_with_image(model, tokenizer, image_path, device="cuda"):
    """Test OCR generation with a real image."""
    print("\n" + "="*50)
    print(f"TEST: OCR generation with image: {image_path}")
    print("="*50)

    try:
        result = model.infer(
            tokenizer=tokenizer,
            prompt="<image>\nFree OCR.",
            image_file=image_path,
            output_path="/tmp/ocr_debug_out",
            eval_mode=True,
        )
        print(f"Result type: {type(result)}")
        print(f"Result length: {len(result) if result else 0}")
        print(f"Result (first 200 chars): {str(result)[:200]}")
    except Exception as e:
        import traceback
        print(f"ERROR: {e}")
        traceback.print_exc()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", default=None, help="Path to image for OCR test")
    parser.add_argument("--text-only", action="store_true", help="Test LM only (no image)")
    parser.add_argument("--model-id", default="deepseek-ai/DeepSeek-OCR-2", help="Model ID")
    parser.add_argument("--device", default="cuda:0")
    args = parser.parse_args()

    print(f"Loading model: {args.model_id}")
    print(f"Device: {args.device}")

    from transformers import AutoTokenizer, AutoModelForCausalLM
    import torch

    tokenizer = AutoTokenizer.from_pretrained(args.model_id, trust_remote_code=True)
    print(f"Tokenizer loaded. EOS: {tokenizer.eos_token_id}, vocab: {tokenizer.vocab_size}")

    # Use dtype= (not torch_dtype=) for transformers>=5.0 compat
    from transformers import AutoModel
    model = AutoModel.from_pretrained(
        args.model_id,
        trust_remote_code=True,
        dtype=torch.bfloat16,
    ).to(args.device)
    model.eval()

    # Check weight stats
    first_layer = model.model.layers[0]
    w = first_layer.self_attn.q_proj.weight
    print(f"\nFirst layer q_proj weight stats: mean={w.mean():.4f}, std={w.std():.4f}")
    print(f"LM head weight stats: mean={model.lm_head.weight.mean():.4f}, std={model.lm_head.weight.std():.4f}")

    if args.text_only or args.image is None:
        test_lm_only(model, tokenizer, args.device)
    else:
        test_lm_only(model, tokenizer, args.device)
        test_with_image(model, tokenizer, args.image, args.device)


if __name__ == "__main__":
    main()
